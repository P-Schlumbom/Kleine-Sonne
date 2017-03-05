import json
import numpy as np

class FNN:
    def create_weights(self, size):
        return [np.random.uniform(-1, 1) for i in range(size)]

    def __init__(self, nLayers, nInFeat, nOutFeat, filename=None):
        self.filename = filename
        self.nLayers = nLayers
        self.nInFeat = nInFeat
        self.nOutFeat = nOutFeat

        self.nHidden = int((nInFeat+nOutFeat)/2)
        nHidden = self.nHidden

        self.eta = 0.1  # learning rate



        x = [[[0, 0] for i in range(nInFeat)],[]]  # input features
        x[0].append([1, 0])  # bias node for the hidden layer (where x = pval = 1 always)
        h = []
        for i in range(nLayers - 2):  # add a list item for every hidden layer, but not the input and output layers
            h.append([[[0, 0] for j in range(nHidden)],[]])
            h[i][0].append([1, 0])  # bias node for the next layer (where x = pval = 1 always)
            if i == 0:
                h[i][1] = [self.create_weights(nInFeat + 1) for j in range(nHidden)]  # the first hidden layer has nInFeat input weights for each neuron
            else:
                h[i][1] = [self.create_weights(nHidden + 1) for j in range(nHidden)]  # all other hidden layers have nHidden input weights for each neuron
        #w1 = []  # set of weight sets going from input layer to first hidden layer
        #h1 = []  # first hidden layer
        #w2 = []  # set of weight sets going from first hidden layer to output
        y = [[[0,0] for i in range(nOutFeat)],[self.create_weights(nHidden + 1) for i in range(nOutFeat)]]  # output feature. y[0] is the list of outputs of the network, y[1] contains the incoming weights associated with each output neuron

        try:
            with open(filename) as f:
                strIn = f.read()
            data = json.loads(strIn)
            x, h, y = data[0], data[1], data[2]
            #for i in range(nLayers - 2):
            #    h[i][1] = data[i]
            #y[1] = data[len(data) - 1]
        except:
            print("Memory unavailable, generating new weights")

        self.x, self.h, self.y = x, h, y

    def logistic_activation_function(self, sum_of_weights):
        x = np.power(np.e, sum_of_weights)
        pval = 1 / (1 + x)
        return pval

    def predict(self, inputData):
        """
        given a list of input variables, use the network to calculate the output
        :param inputData: list of input features (as floats between 0 and 1)
        :return: list of float outputs, one pval for each neuron in the output layer (y layer)
        """
        self.x[0] = [[i, 0] for i in inputData]  # 0th element of each node is the pval
        self.x[0].append([1, 0])  # bias node for the hidden layer (where x = pval = 1 always)

        for i in range(self.nHidden):
            pval1 = 0
            for j in range(self.nInFeat + 1):  # for every node in h1, calculate the sum of the ingoing weights multiplied by the pval of each ingoing neuron (incöuding the bias node)
                pval1 += self.h[0][1][i][j] * self.x[0][j][0]
            self.h[0][0][i][0] = self.logistic_activation_function(pval1)  # update the pval for h1 neuron i

        for k in range(1, self.nLayers - 2):
            #self.h[i][0] = [[j, 0] for j in ]
            for i in range(self.nHidden):
                pval1 = 0
                for j in range(self.nHidden + 1):  # for every node in h1, calculate the sum of the ingoing weights multiplied by the pval of each ingoing neuron (incöuding the bias node)
                    pval1 += self.h[k][1][i][j] * self.h[k-1][0][j][0]
                self.h[k][0][i][0] = self.logistic_activation_function(pval1)  # update the pval for h1 neuron i

        for i in range(self.nOutFeat):
            pval1 = 0
            for j in range(self.nHidden + 1):  # for every node in h, calculate the sum of the ingoing weights multiplied by the pval of each ingoing neuron (incöuding the bias node)
                pval1 += self.y[1][i][j] * self.h[len(self.h) - 1][0][j][0]
            self.y[0][i][0] = self.logistic_activation_function(pval1)  # update the pval for y neuron i

        return [n[0] for n in self.y[0]]

    def train(self, actualResult):
        """
        given desired result of last calculation, update all errors and weights of the network accordingly
        :param actualResult: a list of floats representing the correct answers
        :return:
        """
        # ------------------------this section handles backpropagation of errors--------------------#
        # error of output:
        # y[1] = y[0] * (1 - y[0]) * (y[0] - actual_result)  # y[1] <= err = pval*(1 - pval)*(pval - val)
        self.y[0] = [[self.y[0][i][0], self.y[0][i][0] * (1 - self.y[0][i][0]) * (self.y[0][i][0] - actualResult[i])] for i in range(len(self.y[0]))]

        for i in range(len(self.h[len(self.h) - 1][0])):  # for each neuron of the bottommost hidden layer, updated by the output neuron values
            pval = self.h[len(self.h) - 1][0][i][0]
            self.h[len(self.h) - 1][0][i][1] = pval * (1 - pval) * (np.sum([(self.y[1][j][i] * self.y[0][j][1]) for j in range(len(self.y[0]))]))  # pval * (1 - pval) * (sum of (weight from y to this particular node)*(error of y) for each node in y)

        for k in range(len(self.h) - 2, -1, -1):  # h[len(h) - 2::-1]:
            for i in range(len(self.h[k][0]) - 1):
                pval = self.h[k][0][i][0]
                self.h[k][0][i][1] = pval * (1 - pval) * (np.sum(
                    [(self.h[k + 1][1][i][j] * self.h[k + 1][0][i][1]) for j in range(len(
                        self.h[k + 1][0]))]))  # pval * (1 - pval) * (sum of (weight from h[k+1] (the previous hidden layer) to this particular node)*(error of h[k+1]) for each node in y)

        for i in range(len(self.x[0][len(self.x[0]) - 1])):
            pval = self.x[0][i][0]
            self.x[0][i][1] = pval * (1 - pval) * (np.sum(
                    [(self.h[0][1][i][j] * self.h[0][0][i][1]) for j in range(len(
                        self.h[0][0]))]))
        # --------------------------end of backpropagation section----------------------------------#

        # --------------------------this section adjusts the weights according to the errors--------#
        for i in range(len(self.h)):  # for every hidden layer
            for j in range(len(self.h[i][1])):   # for every set of weights per neuron of layer i
                for k in range(len(self.h[i][1][j])):  # for every weight to neuron j of layer i
                    self.h[i][1][j][k] += (self.eta * self.h[i][0][j][1] * self.h[i][0][j][0])  # given parent node v (here input feature x[j]), update the weight from v to h1[i] with (eta*err(h1[i])*pval(h1[i]))

        for j in range(len(self.y[1])):  # for every set of weights per neuron of the output layer
            for k in range(len(self.y[1][j])):  # for every weight to neuron j of the output layer
                self.y[1][j][k] += (self.eta * self.y[0][j][1] * self.y[0][j][0])  # update this weight with j's error and predicted value

        # -----------------------------end of weight adjustment section------------------------------#

        if self.filename != None:  # if using external memory file, update it
            toStore = [self.x, self.h, self.y]
            with open(self.filename, 'w') as f:
                str_out = json.dumps(toStore)
                f.write(str_out)

    def multiple_train(self, actualResult, cycles):
        for i in range(cycles):
            self.train(actualResult)

    def quick_train(self, inputData, expectedResult):
        self.train(expectedResult)
        while np.average([np.abs(self.y[0][i][0] - expectedResult[i]) for i in range(len(expectedResult))]) > 0.5:
            self.train(expectedResult)
            self.predict(inputData)

    def __repr__(self):
        global x
        global h
        global y
        out = str(x[0]) + "\n"
        for layer in h:
            out += str(layer[0]) + "\n"
        out += str(y[0]) + "\n"
        return out


    def __str__(self):
        out = str(self.x[0]) + "\n"
        for layer in self.h:
            out += str(layer[0]) + "\n"
        out += str(self.y[0]) + "\n"
        return out

