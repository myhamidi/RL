import EnvGrid
import Agt
import Render

### Parameter:
GZx = 10
GZy = 10

### Init
Env = EnvGrid.clsEnvironment(GZx,GZy,-1)
Agt = Agt.clsAgent(Env.ReturnActionList())
Rnr = Render.clsGrid(GZx,GZy,"")

### Config
Env.SetTerminalState((0,0)); Env.SetRewardAtState((0,0),0)
Env.SetTerminalState((GZx-1,GZy-1)); Env.SetRewardAtState((GZx-1,GZy-1),0)
Env.SetStartPosition((int(GZx/2),int(GZy/2)))

### Train
c = 0; runs_train = 3000
while c < runs_train:
    Agt.PerceiveState(Env.RetState(),Env.RetReward())
    if Env.IsCurrentStateTerminal():
        c+=1
        Env.Reset()
    if c%100 == 0: 
        print("Train Step: " + str(c),end ='\r')
    eps = 1-c/runs_train
    Env.Next(Agt.NextAction(eps))

### Test
tmpState = ""; c = 0; runs_train = 10 #2*(GZ-1)
Env.SetRandomStart()
while c < runs_train:
    Agt.TakeState(Env.RetState(),Env.RetReward())
    # Env.render(0.01,"InTKinter")   #"InConsole"
    if Env.RetState() == tmpState:
        print("error - No State Change during Test " + tmpState + " " + str(c))
        break
    tmpState = Env.RetState()
    Rnr.renderArray(Env.RetGridAsArray(),Env.RetState(),50)
    if Env.IsCurrentStateTerminal():
        tmpState = ""; c+=1
        Env.Reset()
        Env.SetRandomStart()
    eps = 0
    Env.Next(Agt.NextAction(eps))

### Print Results
Agt.printSequence("SeqRews-Grid.csv","w")
Agt.printQ("Q-TrMa.csv","w")


### myTracer
# arr = EnvGrid.tr.getCalls();# print(*arr, sep="\n")