from direct.showbase import GarbageReport
from otp.ai.AIBaseGlobal import *
from otp.ai.MagicWordGlobal import *
from otp.avatar import DistributedAvatarAI
from otp.avatar import PlayerBase
from otp.distributed.ClsendTracker import ClsendTracker
from otp.otpbase import OTPGlobals


class DistributedPlayerAI(DistributedAvatarAI.DistributedAvatarAI, PlayerBase.PlayerBase, ClsendTracker):

    def __init__(self, air):
        DistributedAvatarAI.DistributedAvatarAI.__init__(self, air)
        PlayerBase.PlayerBase.__init__(self)
        ClsendTracker.__init__(self)
        self.friendsList = []
        self.DISLname = ''
        self.DISLid = 0
        self.adminAccess = 0

    if __dev__:

        def generate(self):
            self._sentExitServerEvent = False
            DistributedAvatarAI.DistributedAvatarAI.generate(self)

    def announceGenerate(self):
        DistributedAvatarAI.DistributedAvatarAI.announceGenerate(self)
        ClsendTracker.announceGenerate(self)
        self._doPlayerEnter()

    def _announceArrival(self):
        self.sendUpdate('arrivedOnDistrict', [self.air.districtId])

    def _announceExit(self):
        self.sendUpdate('arrivedOnDistrict', [0])

    def _sendExitServerEvent(self):
        self.air.writeServerEvent('avatarExit', self.doId, '')
        if __dev__:
            self._sentExitServerEvent = True

    def delete(self):
        if __dev__:
            del self._sentExitServerEvent
        self._doPlayerExit()
        ClsendTracker.destroy(self)
        if __dev__:
            GarbageReport.checkForGarbageLeaks()
        DistributedAvatarAI.DistributedAvatarAI.delete(self)

    def isPlayerControlled(self):
        return True

    def setLocation(self, parentId, zoneId):
        DistributedAvatarAI.DistributedAvatarAI.setLocation(self, parentId, zoneId)
        if self.isPlayerControlled():
            if not self.air._isValidPlayerLocation(parentId, zoneId):
                self.notify.info('booting player %s for doing setLocation to (%s, %s)' % (self.doId, parentId, zoneId))
                self.air.writeServerEvent('suspicious', self.doId, 'invalid setLocation: (%s, %s)' % (parentId, zoneId))
                self.requestDelete()

    def _doPlayerEnter(self):
        self.incrementPopulation()
        self._announceArrival()

    def _doPlayerExit(self):
        self._announceExit()
        self.decrementPopulation()

    def incrementPopulation(self):
        self.air.incrementPopulation()

    def decrementPopulation(self):
        simbase.air.decrementPopulation()

    def b_setChat(self, chatString, chatFlags):
        self.setChat(chatString, chatFlags)
        self.d_setChat(chatString, chatFlags)

    def d_setChat(self, chatString, chatFlags):
        self.sendUpdate('setChat', [chatString, chatFlags])

    def setChat(self, chatString, chatFlags):
        pass

    def d_setMaxHp(self, maxHp):
        DistributedAvatarAI.DistributedAvatarAI.d_setMaxHp(self, maxHp)
        self.air.writeServerEvent('setMaxHp', self.doId, '%s' % maxHp)

    def d_setSystemMessage(self, aboutId, chatString):
        self.sendUpdate('setSystemMessage', [aboutId, chatString])

    def d_setCommonChatFlags(self, flags):
        self.sendUpdate('setCommonChatFlags', [flags])

    def setCommonChatFlags(self, flags):
        pass

    def d_friendsNotify(self, avId, status):
        self.sendUpdate('friendsNotify', [avId, status])

    def friendsNotify(self, avId, status):
        pass

    def setAccountName(self, accountName):
        self.accountName = accountName

    def getAccountName(self):
        return self.accountName

    def setDISLid(self, id):
        self.DISLid = id

    def getDISLid(self):
        return self.DISLid

    def d_setFriendsList(self, friendsList):
        self.sendUpdate('setFriendsList', [friendsList])

    def setFriendsList(self, friendsList):
        self.friendsList = friendsList
        self.notify.debug('setting friends list to %s' % self.friendsList)

    def getFriendsList(self):
        return self.friendsList

    def setAdminAccess(self, access):
        self.adminAccess = access

    def d_setAdminAccess(self, access):
        self.sendUpdate('setAdminAccess', [access])

    def b_setAdminAccess(self, access):
        self.setAdminAccess(access)
        self.d_setAdminAccess(access)

    def getAdminAccess(self):
        return self.adminAccess

    def extendFriendsList(self, friendId, friendCode):
        for i in xrange(len(self.friendsList)):
            friendPair = self.friendsList[i]
            if friendPair[0] == friendId:
                self.friendsList[i] = (friendId, friendCode)
                return

        self.friendsList.append((friendId, friendCode))


@magicWord(category=CATEGORY_ADMINISTRATOR, types=[str])
def system(message):
    """
    Broadcasts a message to the server.
    """
    # TODO: Make this go through the UberDOG, rather than the AI server.
    for doId, do in simbase.air.doId2do.items():
        if isinstance(do, DistributedPlayerAI):
            if str(doId)[0] != str(simbase.air.districtId)[0]:
                do.d_setSystemMessage(0, message)

@magicWord(category=CATEGORY_ADMINISTRATOR, types=[str, str, int])
def accessLevel(accessLevel, storage='PERSISTENT', showGM=1):
    """
    Modify the target's access level.
    """
    accessName2Id = {
        'user': CATEGORY_USER.defaultAccess,
        'u': CATEGORY_USER.defaultAccess,
        'communitymanager': CATEGORY_COMMUNITY_MANAGER.defaultAccess,
        'community': CATEGORY_COMMUNITY_MANAGER.defaultAccess,
        'c': CATEGORY_COMMUNITY_MANAGER.defaultAccess,
        'moderator': CATEGORY_MODERATOR.defaultAccess,
        'mod': CATEGORY_MODERATOR.defaultAccess,
        'm': CATEGORY_MODERATOR.defaultAccess,
        'creative': CATEGORY_CREATIVE.defaultAccess,
        'creativity': CATEGORY_CREATIVE.defaultAccess,
        'c': CATEGORY_CREATIVE.defaultAccess,
        'programmer': CATEGORY_PROGRAMMER.defaultAccess,
        'coder': CATEGORY_PROGRAMMER.defaultAccess,
        'p': CATEGORY_PROGRAMMER.defaultAccess,
        'administrator': CATEGORY_ADMINISTRATOR.defaultAccess,
        'admin': CATEGORY_ADMINISTRATOR.defaultAccess,
        'a': CATEGORY_ADMINISTRATOR.defaultAccess,
        'systemadministrator': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        'systemadmin': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        'sysadministrator': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        'sysadmin': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        'system': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        'sys': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        's': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess
    }
    try:
        accessLevel = int(accessLevel)
    except:
        if accessLevel not in accessName2Id:
            return 'Invalid access level!'
        accessLevel = accessName2Id[accessLevel]
    if accessLevel not in accessName2Id.values():
        return 'Invalid access level!'
    target = spellbook.getTarget()
    invoker = spellbook.getInvoker()
    target.b_setAdminAccess(accessLevel)
    if showGM:
        target.b_setGM(accessLevel)
    temporary = storage.upper() in ('SESSION', 'TEMP', 'TEMPORARY')
    if not temporary:
        target.air.dbInterface.updateObject(
            target.air.dbId,
            target.getDISLid(),
            target.air.dclassesByName['AccountAI'],
            {'ACCESS_LEVEL': accessLevel})
    if not temporary:
        target.d_setSystemMessage(0, '{0} set your access level to {1}!'.format(invoker.getName(), accessLevel))
        return "{0}'s access level has been set to {1}.".format(target.getName(), accessLevel)
    else:
        target.d_setSystemMessage(0, '{0} set your access level to {1} temporarily!'.format(invoker.getName(), accessLevel))
        return "{0}'s access level has been set to {1} temporarily.".format(target.getName(), accessLevel)
        
@magicWord(category=CATEGORY_ADMINISTRATOR, types=[str, str, int])
def ownLevel(accessLevel, storage='PERSISTENT', showGM=1):
    """
    Modify the target's access level.
    """
    accessName2Id = {
        'user': CATEGORY_USER.defaultAccess,
        'u': CATEGORY_USER.defaultAccess,
        'communitymanager': CATEGORY_COMMUNITY_MANAGER.defaultAccess,
        'community': CATEGORY_COMMUNITY_MANAGER.defaultAccess,
        'c': CATEGORY_COMMUNITY_MANAGER.defaultAccess,
        'moderator': CATEGORY_MODERATOR.defaultAccess,
        'mod': CATEGORY_MODERATOR.defaultAccess,
        'm': CATEGORY_MODERATOR.defaultAccess,
        'creative': CATEGORY_CREATIVE.defaultAccess,
        'creativity': CATEGORY_CREATIVE.defaultAccess,
        'c': CATEGORY_CREATIVE.defaultAccess,
        'programmer': CATEGORY_PROGRAMMER.defaultAccess,
        'coder': CATEGORY_PROGRAMMER.defaultAccess,
        'p': CATEGORY_PROGRAMMER.defaultAccess,
        'administrator': CATEGORY_ADMINISTRATOR.defaultAccess,
        'admin': CATEGORY_ADMINISTRATOR.defaultAccess,
        'a': CATEGORY_ADMINISTRATOR.defaultAccess,
        'systemadministrator': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        'systemadmin': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        'sysadministrator': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        'sysadmin': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        'system': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        'sys': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess,
        's': CATEGORY_SYSTEM_ADMINISTRATOR.defaultAccess
    }
    try:
        accessLevel = int(accessLevel)
    except:
        if accessLevel not in accessName2Id:
            return 'Invalid access level!'
        accessLevel = accessName2Id[accessLevel]
    if accessLevel not in accessName2Id.values():
        return 'Invalid access level!'
    target = spellbook.getTarget()
    invoker = spellbook.getInvoker()
    invoker.b_setAdminAccess(accessLevel)
    if showGM:
        invoker.b_setGM(accessLevel)
    temporary = storage.upper() in ('SESSION', 'TEMP', 'TEMPORARY')
    if not temporary:
        invoker.air.dbInterface.updateObject(
            invoker.air.dbId,
            invoker.getDISLid(),
            invoker.air.dclassesByName['AccountAI'],
            {'ACCESS_LEVEL': accessLevel})
    if not temporary:
        invoker.d_setSystemMessage(0, '{0} set your access level to {1}!'.format(invoker.getName(), accessLevel))
        return "{0}'s access level has been set to {1}.".format(target.getName(), accessLevel)
    else:
        invoker.d_setSystemMessage(0, '{0} set your access level to {1} temporarily!'.format(invoker.getName(), accessLevel))
        return "{0}'s access level has been set to {1} temporarily.".format(target.getName(), accessLevel)
        
@magicWord(category=CATEGORY_ADMINISTRATOR, types=[int, str, int])
def setGuild(guildNum, storage='PERSISTENT', showGuildBadge=1): #Admin command to set a user's guild, particularly a clan leader to their new guild, leaders can later invite their own members and other leaders by themselves
    target = spellbook.getTarget()
    invoker = spellbook.getInvoker()
    if guildNum <= 99 and guildNum >= 1:
            target.b_setGM(guildNum)
            target.d_setSystemMessage(0, 'Guild ID successfully set to {0} by STAFF MEMBER {1}.'.format(guildNum, invoker.getName()))
            invoker.d_setSystemMessage(0, 'Guild ID successfully set as {0} to user {1}.'.format(guildNum, target.getName()))
    else:
        return "Invalid guild number! 1-99, numeric characters."
        
@magicWord(category=CATEGORY_ADMINISTRATOR, types=[int, str, int])
def myGuild(guildNum, storage='PERSISTENT', showGuildBadge=1): #Allow an admin to set their own guild, this is only used on the person who runs the actual command in the chat
    target = spellbook.getTarget()
    invoker = spellbook.getInvoker()
    if guildNum <= 99999 and guildNum >= 1:
            invoker.b_setGM(guildNum)
            invoker.d_setSystemMessage(0, 'Guild ID successfully set to {0} by yourself, STAFF MEMBER {1}.'.format(guildNum, invoker.getName()))
    else:
        return "Invalid guild number! 1-99, numeric characters."
        
@magicWord(category=CATEGORY_ADMINISTRATOR)
def invite():
    target = spellbook.getTarget() #New Person Being Invited
    invoker = spellbook.getInvoker() #Clan Leader Using Command
    guildId = invoker.getAdminAccess() #Get the guild of the person who RUNS / SENDS the command, obviously
    target.b_setGM(guildId) #Add target to guild, this basically is for badge purposes, staff permissions don't start until 100 (Guilds are 1-99 only, which also obviously avoids all "greater than" permissions for staff ranges)
    invoker.d_setSystemMessage(0, 'You have added user {0} to your guild. They have been notified.'.format(target.getName())) #Let the clan leader know it worked
    target.d_setSystemMessage(0, 'ATTENTION, {0}! Guild Leader {1} has added you to their guild! (Guild ID: {2}) Congratulations!'.format(target.getName(), invoker.getName(), guildId)) #Notify the new member
    target.d_setSystemMessage(0, 'You may leave this guild at any time using ~leaveguild. Have fun!') #New member send message 2
    
