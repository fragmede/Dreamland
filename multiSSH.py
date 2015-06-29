import paramiko
import sys
import time
import threading

serverIp = "10.0.1.165"

login = "pi"
password = "raspberry"

config = [
    {"hostname": "pi.local", "serverIp": serverIp, "structureName": "carousel"},
    {"hostname": "pi.local", "serverIp": serverIp, "structureName": "bench1"},
    {"hostname": "pi.local", "serverIp": serverIp, "structureName": "bench2"}
]

config2 = {
    "Carousel": {"hostname": "pi.local", "serverIp": serverIp},
    "Bench": {"hostname": "pi.local", "serverIp": serverIp},
    "Bench1": {"hostname": "pi.local", "serverIp": serverIp}
}


def doSomethingHere():
    pass


# simple class that creates an SSH connection to a single computer.
class SSHConnection():
    def __init__(self, hostname, structureName):
        self.hostname = hostname
        self.structureName = structureName
        self.login = login
        self.password = password
        self.connectToSSH()

    # create an SSH connection, while passing errors if they arise.
    def connectToSSH(self):
        for x in range(10):
            try:
                self.ssh = paramiko.SSHClient()
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh.connect(self.hostname, username=login, password=password)
                print ("Connected to " + self.structureName)
                break

            except paramiko.AuthenticationException:
                print ("Authentication failed when connecting to " + self.structureName)
                sys.exit(1)

            except:
                print ("Could not SSH to " + self.structureName + ", waiting for it to start")
                time.sleep(1)
        return

        # If no connection in the allowed time.
        raise RuntimeError("Could not connect to " + self.structureName + ". Giving up")

    def connectToSSHThreaded(self, threadName):
        threading.Thread(target=self.connectToSSH(), name=threadName).start()

    # once an SSH connection is created, then it is time to issue commands over the tubes
    def runCommand(self, commandToRun):
        stdin, stdout, stderr = self.ssh.exec_command(commandToRun)


# Now lets make multiple ssh connections to a list of computers
class MultiSSH:
    def __init__(self, configDict):
        self.configDict = configDict
        self.structureNames = list(self.configDict.keys())
        self.sshConnections = []
        for structure in self.structureNames:
            self.sshConnections.append(SSHConnection(self.configDict[structure]["hostname"], structure))

    def runOnAll(self, commandToRun):
        for connection in self.sshConnections:
            connection.connectToSSH.runCommand(commandToRun)

    def runOnGroup(self, groupDescriptor, commandToRun):
        pass

    def runMultipleCommandsOnAll(self, commandList):
        pass

    def setupConfigFile(self):
        configName = "structureConfig"
        for connection in self.sshConnections:
            name = connection.structureName
            e = echo(configName, self.configDict[name], name)
            commandsToWrite = e.writeConfig()

            for index in range(len(commandsToWrite)):
                command = commandsToWrite[index]
                print(command)
                connection.runCommand(command)


# Take a dictionary and parse out the correct string to send echo commands over the ssh connection
class echo:
    def __init__(self, fileName, configDict, name):
        self.fileName = fileName
        self.configDict = configDict
        self.structureName = name

    def writeConfig(self):
        fileLocation = '~/repo/Dreamland/' + self.fileName + '.py'

        keys = list(self.configDict.keys())

        configToWrite = []
        string = """echo %s = {"'%s'": "'%s'",  > %s""" % (self.fileName, "structureName", self.structureName, fileLocation)
        configToWrite.append(string)

        for index, key in enumerate(keys):
            if index == len(keys) - 1:
                string = """echo "'%s'": "'%s'"}  >> %s""" % (key, self.configDict[key], fileLocation)
            else:
                string = """echo "'%s'": "'%s'",  >> %s""" % (key, self.configDict[key], fileLocation)

            configToWrite.append(string)

        return configToWrite
