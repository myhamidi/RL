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
# Env.SetTerminalState((GZx-1,GZy-1)); Env.SetRewardAtState((GZx-1,GZy-1),0)
Env.SetStartPosition((int(GZx/2),int(GZy/2)))
Agt.setLearningParameter(0.2,1)

### Train
c = 0; runs_train = 3000
while c < runs_train:
    Agt.perceiveState(Env.RetStateFeatures(), Env.RetReward())
    if Env.IsCurrentStateTerminal():
        c+=1
        Env.Reset()
    eps = 1-c/runs_train
    Env.Next(Agt.nextAction(eps))
    if c%100 == 0:print("Train Step: " + str(c),end ='\r')

### Test
tmpState = ""; c = 0; runs_test = 5;imax = 20;i=0 #2*(GZ-1);
Env.SetRandomStart()
while c < runs_test and i < imax:
    Agt.getState(Env.RetStateFeatures(), Env.RetReward())
    # Env.render(0.01,"InTKinter")   #"InConsole"
    Rnr.renderArray(Env.RetGridAsArray(),Env.RetState(),50)
    assert not Env.RetState() == tmpState,"No State Change during Test. State is: " + tmpState 
    i +=1
    tmpState = Env.RetState()
    if Env.IsCurrentStateTerminal():
        tmpState = ""; c+=1;i=0
        Env.Reset()
        Env.SetRandomStart()
    eps = 0
    Env.Next(Agt.nextAction(eps))

Agt.RoundQ(2)
Agt.CreateQListFromQTable()

# tmpQ = Agt.RetQTable()
# tmpStates = Agt.RetFeatStates()
# tmpQList = Agt.RetQList()
# Agt.reset()
# Agt.ImportQTable(tmpStates,tmpQ)
# Agt.ImportQList(tmpQList)
# arr = Agt.Importcsv("Q-Grid.csv")

### Print Results
# Agt.printSequence100("csv/SeqRews-Grid.csv","w")
Agt.printQTable("csv/Q-Grid.csv","w")
Agt.printQList("csv/QList-Grid.csv","w")

### myTracer
# arr = EnvGrid.tr.getCalls(); print(*arr, sep="\n")