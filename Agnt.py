# ==============================================================================
# -- API -----------------------------------------------------------------------
#
# Agnt.clsAgent(["jump", "run"],["world","level","terminal"])   | Initiate Agent
# Agt.SetParameter(["alpha","gamma"],[0.8,0.99])                | Set Agents parameter
# Agt.PerceiveEnv([2,"street",0.1,0],-2)                        | Agent State and Reward Preception. Last index of list:
#                                                               | 0 = non terminal; 1 = terminal state
# Agt.Reset()                                                   | Delete Agt internal states and sequeces


import random
from numpy.random import choice as npchoice
import pandas as pd

class typState:
    def __init__(self, features = [] , reward = 0.0, Q = [], QUpdates = 0):
        self.features = features
        self.reward = [reward, reward]
        self.Q = Q
        self.QUpdates = QUpdates

class typStep:
    def __init__(self, state0 = [0], state1 = [0] , reward = 0, totalreward = 0.0, actionInt = -1, action = "", rg = "r"):
        self.state0 = state0
        self.state1 = state1
        self.reward = reward                # reward of state0
        self.totalreward = totalreward      # totalreward of state0. if terminal totalreward of state1
        self.actionInt = actionInt
        self.action = action
        self.rg = rg
        self.StepSampled = 0

class clsAgent:
#Public:
    def __init__(self, actionlist, featurelist = []):
        self.States = []         #Typ: typState. Remembers all (unique) states qUpdated.
        self.Sequence = []
        self.TerminalRewards = []       # idx, reward
        self.actions = actionlist
        self.actionsConstrains = actionlist
        self.features = featurelist
        self.Nterminal = 0

        self.alpha = .1
        self.gamma = 1.0
        self.epsilon = 1.0
        self.randIdx = 0
        self.rand1000 = list(range(1000));random.shuffle(self.rand1000)
        self.FitDQNStepSize = 10
        self.DQNCounter = 0
        self.ModelAlpha = 0.001

        self.batchsize = 0
        self.SequenceSampleLIST = []
        self.SequenceSampleLISTXA = []
        self.SequenceSampleLISTX = []
        self.SequenceSampleTYP = []

# ==============================================================================
# -- Init ----------------------------------------------------------------------
# ==============================================================================   
    def SetParameter(self, parameter = [],value = []):
        assert len(parameter)>0 and len(parameter)== len(value)
        for i in range(len(parameter)):
            if parameter[i] == "alpha":self.alpha = value[i]
            if parameter[i] == "gamma":self.gamma = value[i]
            if parameter[i] == "epsilon":
                assert len(value[i]) == 1 or len(value[i]) == len(self.actions)+1
                if len(value[i]) > 1:
                    assert sum(value[i]) == 1 + value[i][0]
                self.epsilon = value[i]


# ==============================================================================
# -- Perception ----------------------------------------------------------------
# ============================================================================== 
    def PerceiveEnv(self,state,reward):
        self._UpdateSequence(state)
        self._UpdateStatesTable(state)
        self._RewardToStep(reward)
        # self._UpdateNumTerminal()

        
    def _UpdateSequence(self,featState):
        if len(self.Sequence)==0:
            self.Sequence.append(typStep(state0 = featState))
            return

        if featState[-1] == 0:
            self.Sequence.append(typStep(state0 = featState))
            if self.Sequence[-2].state1 == [0]:self.Sequence[-2].state1 = featState 
        else:
            self.Sequence[-1].state1 = featState
    
    def _UpdateStatesTable(self,state):
        for i in range(len(self.States)):
             if state == self.States[i].features: 
                return
        self.States.append(typState(features = state, Q =[0]*len(self.actions)))

# ==============================================================================
# -- Reward ----------------------------------------------------------------
# ============================================================================== 

    def _RewardToStep(self,reward):
        self.Sequence[-1].reward = self._RetReward(reward)
        self.Sequence[-1].totalreward = self._RetTotalReward(reward)

    def _RetReward(self,reward):
        if self.Sequence[-1].state1[-1] == 1:
            return self.Sequence[-1].reward
        return reward 
    
    def _RetTotalReward(self,reward):
        if len(self.Sequence) == 1 and self.Sequence[-1].state1[-1] == 0:
            return reward
        if len(self.Sequence) == 1 and self.Sequence[-1].state1[-1] == 1:
            return self.Sequence[-1].reward + reward
        if self.Sequence[-2].state1[-1] == 1:
            return reward
        if self.Sequence[-1].state1[-1] == 1:
            return self.Sequence[-1].totalreward + reward 
        return self.Sequence[-2].totalreward + reward 


    def Reset(self):
        self.States = []
        self.Sequence = []

# ==============================================================================
# -- Return ---------------------------------------------------------------------
# ==============================================================================     
    def Info(self):
        retStr = "Actions: " + str(self.actions) +"\n"
        retStr += "State Features: " + str(self.features)
        return retStr

# ==============================================================================
# -- Actions -------------------------------------------------------------------
# ==============================================================================  
    def NextAction(self):
        retNextAction = self._RetRandomAction() if self._NextActionIsRandom() else ""
        self._SetActionToLastStep(retNextAction)
        return retNextAction

    def _NextRand1000(self):
        self.randIdx +=1
        if self.randIdx == 1000: self.randIdx = 0
        return self.rand1000[self.randIdx]

    def _RetRandomAction(self):
        if len(self.epsilon)>1:
            return npchoice(a=self.actions,size=1,p=self.epsilon[1:])[0]
        else:
            return random.choice(self.actions)

    def _SetActionToLastStep(self,action):
        self.Sequence[-1].action = action
    
    def _NextActionIsRandom(self):
        rand = self._NextRand1000()/1000
        if rand <= self.epsilon[0]: # Random (x-case epsilon == 1)
            return True
        else:
            return False

# ==============================================================================
# -- Import --------------------------------------------------------------------
# ==============================================================================
    def ImportQ(self,dataset_path, ResetStates = True):
        if ResetStates:self.States = []
        QImport = pd.read_csv(dataset_path, skiprows = 0, na_values = "?", \
        comment='\t', sep="|", skipinitialspace=True, error_bad_lines=False)

        for col, _ in QImport.iterrows():
            features = QImport.at[col, "State"].replace("[","").replace("]","").split(",")
            Q = QImport.at[col, "Q"].replace("[","").replace("]","").split(",")
            QUpdates = QImport.at[col, "QUpdates"]
            for i in range(len(features)): features[i] = float(features[i])
            for i in range(len(Q)): Q[i] = float(Q[i])
            self.States.append(typState(features = features, Q = Q, QUpdates = QUpdates))

    def ImportSeq(self,dataset_path, ResetSequence = True):
        if ResetSequence:self.Sequence = []
        SeqImport = pd.read_csv(dataset_path, skiprows = 0, na_values = "?", \
        comment='\t', sep="|", skipinitialspace=True, error_bad_lines=False)

        for col, _ in SeqImport.iterrows():
            state0 = SeqImport.at[col, "state0"].replace("[","").replace("]","").split(",")
            state1 = SeqImport.at[col, "state1"].replace("[","").replace("]","").split(",")
            r = SeqImport.at[col, "reward"]
            tr = SeqImport.at[col, "treward"]
            a = SeqImport.at[col, "action"]
            aint = SeqImport.at[col, "actionInt"]
            rg = SeqImport.at[col, "rnd_gd"]
            for i in range(len(state0)): state0[i] = float(state0[i])
            for i in range(len(state1)): state1[i] = float(state1[i])
            self.Sequence.append(typStep(state0=state0,state1=state1, \
                reward=r, totalreward=tr, action = a, actionInt = aint, rg= rg))

# ==============================================================================
# -- Export --------------------------------------------------------------------
# ==============================================================================
    def ExportQtoCSV(self, path, SplitCols = False):
        Qpd = pd.DataFrame()
        Qpd["State"] = [state.features for state in self.States]
        Qpd["Q"] = [state.Q for state in self.States]
        Qpd["QUpdates"] = [state.QUpdates for state in self.States]
        
        if SplitCols:
            Qlistpd = pd.DataFrame()
            new = pd.DataFrame(Qpd["State"].values.tolist())  
            for i in range(len(new.columns)-1):
                Qlistpd["Statefeat"+str(i)] = new[i]
            Qlistpd["terminal"] = new[len(new.columns)-1]
            new = pd.DataFrame(Qpd["Q"].values.tolist(), columns = self.actions)  
            Qlistpd = pd.concat([Qlistpd, new], axis=1, sort=False)
            Qlistpd["QUpdates"] = Qpd["QUpdates"]
            Qlistpd.to_csv(path, sep='|', encoding='utf-8', index = False)
        else:
            Qpd.to_csv(path, sep='|', encoding='utf-8', index = False)

        
    def ExportSeqtoCSV(self, path, SplitCols = False, nthEpoch = 100):
        nthEpoch = nthEpoch-1
        # Create full size data frame
        Seqpd = pd.DataFrame()
        Seqpd["state0"] = [step.state0 for step in self.Sequence]
        Seqpd["actionInt"] = [step.actionInt for step in self.Sequence]
        Seqpd["action"] = [step.action for step in self.Sequence]
        
        if SplitCols == True:
            for i in range(len(self.actions)):
                Seqpd["blaction"+str(i)] = 0
            for index, row in Seqpd.iterrows():
                for i in range(len(self.actions)):
                    if row["actionInt"] == i: 
                        Seqpd.at[index, "blaction"+str(i)] = 1
        
        Seqpd["state1"] = [step.state1 for step in self.Sequence]
        Seqpd["reward"] = [step.reward for step in self.Sequence]
        Seqpd["treward"] = [step.totalreward for step in self.Sequence]
        Seqpd["rnd_gd"] = [step.rg for step in self.Sequence]
        Seqpd["sampled"] = [step.StepSampled for step in self.Sequence]

        #Create 100evenly distributed indices from 0 to n terminal states-> arr
        arr0 = []; arr1 = []; SeqidxTerminals = []
        for i in range(len(self.Sequence)):
            if self.Sequence[i].state0[-1] == 1:
                SeqidxTerminals.append(i)
        if len(SeqidxTerminals) > nthEpoch:
            for i in range(nthEpoch): 
                idx = int(i * len(SeqidxTerminals)/nthEpoch)
                arr0.append(SeqidxTerminals[idx])
                arr1.append(SeqidxTerminals[idx+1])

            #Mark all lines between index arr[i] - arr[i+1]
            Seqpd["mark"] = 0
            for i in range(nthEpoch):
                for j in range(arr0[i]+1, arr1[i]+1):
                    Seqpd.at[j, "mark"] = 1
                
            # Filter data frame
            Seq100pd =  Seqpd[Seqpd["mark"] == 1]
            Seq100pd = Seq100pd.drop(columns = ["mark"])

            # WRITE TO FILE:
            Seq100pd.to_csv(path, sep='|', encoding='utf-8', index = False)
        else:
            Seqpd.to_csv(path, sep='|', encoding='utf-8', index = False)
