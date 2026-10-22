import sys
p = "/Users/marcelohanones/Developer/personal/ParallelProse2/tools/auto_critique/laco_hammerspoon.lua"
t = open(p, encoding="utf-8").read()
mode = sys.argv[1]  # "on" ou "off"
ON = ['appElem:setAttributeValue("AXEnhancedUserInterface", true)', 'appElem:setAttributeValue("AXManualAccessibility", true)']
if mode == "on":
    anchor = "\n  local appElem = ax.applicationElement(app)\n"
    n = t.count(anchor)
    assert n == 2, n
    t = t.replace(anchor, anchor + "  " + ON[0] + "\n  " + ON[1] + "\n")
else:
    for line in ON:
        t = t.replace("\n  " + line + "\n", "\n")
open(p, "w", encoding="utf-8").write(t)
print("flags", mode, "ok")
