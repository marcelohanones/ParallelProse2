require("hs.ipc")

-- Temporizadores precisam ficar referenciados até dispararem, senão o Lua pode coletá-los e o passo some em silêncio.
local _doAfter = hs.timer.doAfter
local _aliveTimers = {}
hs.timer.doAfter = function(sec, fn)
  local t
  t = _doAfter(sec, function()
    _aliveTimers[t] = nil
    fn()
  end)
  _aliveTimers[t] = true
  return t
end
local ax = require("hs.axuielement")


-- Laço: contagem de rodadas, limite e atalho de emergência. Estado só aqui, fora dos modelos.
local loop = { active = false, rounds = 0, maxRounds = 5 }
local logFile = "/tmp/loop_log.txt"

local function logLine(text)
  local f = io.open(logFile, "a")
  local now = hs.timer.secondsSinceEpoch()
  if f then f:write(os.date("%H:%M:%S ", math.floor(now)) .. string.format("%03d ", math.floor((now % 1) * 1000)) .. text .. "\n") f:close() end
end

-- Marca o tempo decorrido desde t0 (início da etapa), em milissegundos.
local function markLine(t0, text)
  logLine(string.format("%s [+%dms]", text, math.floor((hs.timer.secondsSinceEpoch() - t0) * 1000)))
end

local flagFile = "/tmp/loop_on"

function loopStart()
  loop.active = true
  loop.rounds = 0
  local f = io.open(flagFile, "w")
  if f then f:write("on") f:close() end
  logLine("laco iniciado, limite " .. loop.maxRounds)
  markDshBaseline()
end

function loopStop(reason)
  loop.active = false
  os.remove(flagFile)
  logLine("laco parado: " .. (reason or "manual"))
end

hs.hotkey.bind({"ctrl", "alt", "cmd"}, "s", function()
  loopStop("atalho de emergencia")
  hs.alert.show("Laço parado")
end)

-- Traz o dsh para frente e espera o foco chegar nele (até ~4s). Só então chama onReady.
local function waitDshFocus(app, dshWin, tries, onReady)
  app:activate()
  pcall(function() dshWin:performAction("AXRaise") end)
  hs.timer.doAfter(0.4, function()
    local fw = hs.window.focusedWindow()
    local fwTitle = fw and fw:title() or ""
    if string.find(fwTitle, "DeepSeek Harness", 1, true) then return onReady() end
    if tries <= 1 then
      logLine("cctodsh: abortado, janela focada nao e a do dsh (focada=" .. fwTitle .. ")")
      return
    end
    waitDshFocus(app, dshWin, tries - 1, onReady)
  end)
end

-- Claude Code -> dsh: cola a resposta do Claude no campo do dsh, com as mesmas guardas do teste.
local function forwardToDsh()
  local app = hs.application.get("Google Chrome")
  if not app then logLine("cctodsh: Chrome nao esta rodando") return end
  local fh = io.open("/tmp/cc_last_answer.txt", "r")
  local clip = fh and fh:read("*a") or ""
  if fh then fh:close() end
  if #clip == 0 then logLine("cctodsh: arquivo da resposta vazio") return end
  hs.pasteboard.setContents(clip)
  local appElem = ax.applicationElement(app)
  appElem:setAttributeValue("AXEnhancedUserInterface", true)
  appElem:setAttributeValue("AXManualAccessibility", true)
  local dshWin = nil
  for _, w in ipairs(appElem:attributeValue("AXWindows") or {}) do
    if string.find(w:attributeValue("AXTitle") or "", "DeepSeek Harness", 1, true) then dshWin = w end
  end
  if not dshWin then logLine("cctodsh: janela do dsh nao encontrada") return end
  waitDshFocus(app, dshWin, 10, function()
    local field = nil
    local function walk(el, depth)
      if field or depth > 60 then return end
      for _, k in ipairs(el:attributeValue("AXChildren") or {}) do
        local d = k:attributeValue("AXDescription") or ""
        if k:attributeValue("AXRole") == "AXTextArea" and (string.find(d, "Message or run a task", 1, true) or string.find(d, "Describe what you want to build", 1, true)) then field = k return end
        walk(k, depth + 1)
        if field then return end
      end
    end
    walk(dshWin, 0)
    if not field then logLine("cctodsh: campo do dsh nao encontrado") return end
    local draft = field:attributeValue("AXValue") or ""
    if #(draft:gsub("%s", "")) > 0 then logLine("cctodsh: abortado, campo do dsh nao esta vazio") return end
    local baseline = select(1, scanDsh(dshWin))
    field:setAttributeValue("AXFocused", true)
    hs.timer.doAfter(0.6, function()
      hs.eventtap.keyStroke({"cmd"}, "v")
      logLine("cctodsh: Cmd+V enviado ao dsh")
      hs.timer.doAfter(1.0, function()
        logLine("cctodsh: enviando Return ao dsh")
        hs.eventtap.keyStroke({}, "return")
        logLine("cctodsh: resposta do Claude colada e enviada ao dsh (" .. #clip .. " bytes)")
        waitDshAnswer(baseline)
      end)
    end)
  end)
end

hs.urlevent.bind("cctodsh", function()
  if not loop.active then logLine("cctodsh ignorado: laco inativo") return end
  loop.rounds = loop.rounds + 1
  if loop.rounds > loop.maxRounds then
    loopStop("limite de rodadas")
    hs.alert.show("Limite de rodadas atingido")
    return
  end
  logLine("rodada " .. loop.rounds .. ": Claude -> dsh")
  forwardToDsh()
end)

-- Fase 2: dsh -> Claude Code. Só age com o laço ativo, e só cola se o campo Prompt do Claude estiver vazio.

-- Modos de entrega ao Claude, para os testes: CLAUDE_SEND = "axpress" | "return"; CLAUDE_KEYS = "global" | "post".
local CLAUDE_SEND = "return"
local CLAUDE_KEYS = "post"

-- Tecla no Claude: "global" usa keyStroke; "post" posta o evento direto no processo do Claude.
local function pressKey(app, mods, key)
  if CLAUDE_KEYS == "post" then
    local ok, err = pcall(function()
      hs.eventtap.event.newKeyEvent(mods, key, true):post(app)
      hs.eventtap.event.newKeyEvent(mods, key, false):post(app)
    end)
    if ok then return end
    logLine("dshtocc: erro ao postar tecla, usando keyStroke: " .. tostring(err))
  end
  hs.eventtap.keyStroke(mods, key)
end

-- Envio: com "axpress" procura o botão cuja descrição contém "Enviar" e aciona AXPress; sem achar, cai no Return.
local function sendClaude(app, appElem)
  if CLAUDE_SEND == "axpress" then
    local send = nil
    local function walk(el, depth)
      if send or depth > 40 then return end
      for _, k in ipairs(el:attributeValue("AXChildren") or {}) do
        if k:attributeValue("AXRole") == "AXButton" then
          local d = k:attributeValue("AXDescription") or ""
          if string.find(string.lower(d), "enviar", 1, true) then send = k return end
        end
        walk(k, depth + 1)
        if send then return end
      end
    end
    for _, w in ipairs(appElem:attributeValue("AXWindows") or {}) do
      walk(w, 0)
      if send then break end
    end
    if send then
      local ok = pcall(function() send:performAction("AXPress") end)
      logLine("dshtocc: envio por AXPress (" .. (send:attributeValue("AXDescription") or "") .. ", ok=" .. tostring(ok) .. ")")
      return
    end
    logLine("dshtocc: botao Enviar nao encontrado, usando Return")
  end
  pressKey(app, {}, "return")
end

local function forwardToClaude()
  local t0 = hs.timer.secondsSinceEpoch()
  local app = hs.application.get("Claude")
  if not app then logLine("dshtocc: Claude nao esta rodando") return end
  local clip = hs.pasteboard.getContents() or ""
  if #clip == 0 then logLine("dshtocc: clipboard vazio") return end
  markLine(t0, "dshtocc: inicio")
  app:activate()
  hs.timer.doAfter(1.0, function()
    markLine(t0, "dshtocc: Claude ativado")
    local appElem = ax.applicationElement(app)
    appElem:setAttributeValue("AXManualAccessibility", true)
    hs.timer.doAfter(1.0, function()
      local tw = hs.timer.secondsSinceEpoch()
      local field = nil
      local function walk(el, depth)
        if field or depth > 40 then return end
        for _, k in ipairs(el:attributeValue("AXChildren") or {}) do
          if k:attributeValue("AXRole") == "AXTextArea" and k:attributeValue("AXDescription") == "Prompt" then field = k return end
          walk(k, depth + 1)
          if field then return end
        end
      end
      for _, w in ipairs(appElem:attributeValue("AXWindows") or {}) do
        walk(w, 0)
        if field then break end
      end
      markLine(t0, string.format("dshtocc: busca do campo Prompt em %dms", math.floor((hs.timer.secondsSinceEpoch() - tw) * 1000)))
      if not field then logLine("dshtocc: campo Prompt nao encontrado") return end
      local draft = field:attributeValue("AXValue") or ""
      if #(draft:gsub("%s", "")) > 0 then logLine("dshtocc: abortado, campo do Claude nao esta vazio") return end
      local front = hs.application.frontmostApplication()
      if not front or front:name() ~= "Claude" then logLine("dshtocc: abortado, Claude nao esta na frente") return end
      field:setAttributeValue("AXFocused", true)
      hs.timer.doAfter(0.5, function()
        pressKey(app, {"cmd"}, "v")
        hs.timer.doAfter(1.0, function()
          sendClaude(app, appElem)
          markLine(t0, string.format("dshtocc: resposta colada e enviada ao Claude (%d caracteres) [send=%s keys=%s]", #clip, CLAUDE_SEND, CLAUDE_KEYS))
        end)
      end)
    end)
  end)
end


-- dsh -> Claude pelo arquivo de sessão do dsh. Sem userscript e sem servidor.
-- Formato interno do dsh (versão 0.2.0-rc.2): pode mudar em atualizações.
local dshSessionDir = os.getenv("HOME") .. "/.dsh/storages/session_projcache/sessions/"
local dshSessionId = "09057ce0-5200-4eed-ba2e-313e452d8b53"
local dshSessionFile = dshSessionDir .. "session-" .. dshSessionId .. ".json"
local dshLastSeq = nil


local function readDshTurns()
  local f = io.open(dshSessionFile, "r")
  if not f then return nil, "arquivo da sessao nao encontrado" end
  local raw = f:read("*a")
  f:close()
  local ok, data = pcall(hs.json.decode, raw)
  if not ok or type(data) ~= "table" then return nil, "json invalido" end
  local rows = data.record and data.record.rows
  local turns = rows and rows.turnOutline and rows.turnOutline.val and rows.turnOutline.val.turns
  if type(turns) ~= "table" then return nil, "formato inesperado" end
  return turns
end

-- Chamado ao iniciar o laço: marca o último turno como já visto, para não reenviar respostas antigas.
function markDshBaseline()
  local turns, err = readDshTurns()
  if turns and #turns > 0 then dshLastSeq = turns[#turns].seq end
  logLine("baseline dsh: seq " .. tostring(dshLastSeq) .. (err and (" (" .. err .. ")") or ""))
end


-- Volta dsh -> Claude pelo botão Copy da própria resposta (árvore de acessibilidade, sem clique de coordenada).
function dshWindow()
  local app = hs.application.get("Google Chrome")
  if not app then return nil end
  local appElem = ax.applicationElement(app)
  appElem:setAttributeValue("AXEnhancedUserInterface", true)
  appElem:setAttributeValue("AXManualAccessibility", true)
  for _, w in ipairs(appElem:attributeValue("AXWindows") or {}) do
    if string.find(w:attributeValue("AXTitle") or "", "DeepSeek Harness", 1, true) then return w end
  end
  return nil
end

-- Conta os "Completed" e guarda, na ordem da árvore, os marcadores e os botões Copy.
function scanDsh(win)
  local completed, seq = 0, {}
  local function walk(el, depth)
    if depth > 60 then return end
    for _, k in ipairs(el:attributeValue("AXChildren") or {}) do
      local role = k:attributeValue("AXRole") or ""
      if role == "AXStaticText" and (k:attributeValue("AXValue") or "") == "Completed" then
        completed = completed + 1
        table.insert(seq, "done")
      elseif role == "AXButton" and (k:attributeValue("AXDescription") or "") == "Copy" then
        table.insert(seq, k)
      end
      walk(k, depth + 1)
    end
  end
  walk(win, 0)
  return completed, seq
end

local function copyAfterLastDone(seq)
  local lastDone = nil
  for i, e in ipairs(seq) do if e == "done" then lastDone = i end end
  if not lastDone then return nil end
  for i = lastDone + 1, #seq do if seq[i] ~= "done" then return seq[i] end end
  return nil
end

local function copyDshAnswer(win, seq)
  local btn = copyAfterLastDone(seq)
  if not btn then logLine("dsh: botao Copy da resposta nao encontrado") return end
  hs.application.get("Google Chrome"):activate()
  hs.timer.doAfter(0.8, function()
    pcall(function() win:performAction("AXRaise") end)
    hs.timer.doAfter(1.2, function()
      local fw = hs.window.focusedWindow()
      if not fw or not string.find(fw:title() or "", "DeepSeek Harness", 1, true) then
        logLine("dsh: abortado, janela do dsh nao esta focada")
        return
      end
      hs.pasteboard.setContents("")
      btn:performAction("AXPress")
      hs.timer.doAfter(1.5, function()
        local text = hs.pasteboard.getContents() or ""
        if #text == 0 then logLine("dsh: o botao Copy nao colocou nada no clipboard") return end
        logLine("dsh: resposta copiada pelo botao Copy (" .. #text .. " bytes)")
        forwardToClaude()
      end)
    end)
  end)
end

local dshWaitTimer = nil
-- Espera a resposta: quando surge um "Completed" novo, copia a resposta pelo botão Copy.
function waitDshAnswer(baseline)
  local t0 = hs.timer.secondsSinceEpoch()
  local function tick()
    if not loop.active then return end
    if hs.timer.secondsSinceEpoch() - t0 > 240 then
      logLine("dsh: tempo esgotado esperando a resposta")
      loopStop("tempo esgotado")
      return
    end
    local t1 = hs.timer.secondsSinceEpoch()
    local win = dshWindow()
    if not win then logLine("dsh: janela nao encontrada") return end
    local completed, seq = scanDsh(win)
    logLine(string.format("varredura dsh: %.2fs, completed=%d, base=%d", hs.timer.secondsSinceEpoch() - t1, completed, baseline))
    if completed > baseline then
      copyDshAnswer(win, seq)
    else
      dshWaitTimer = hs.timer.doAfter(2.0, tick)
    end
  end
  dshWaitTimer = hs.timer.doAfter(2.0, tick)
end
