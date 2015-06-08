''' TCP Server '''
import socket
import sys
import thread

class User(object):
    def __init__(self, username, password, admin):
        self.username = username
        self.password = password
        self.online = False
        self.unread_message_list = []
        self.subscribed_to_list = ["a", "b", "c"]
        self.connection = None
        self.client_address = 0
        self.admin = admin
        
userA = User("a", "aa", False)
userB = User("b", "bb", False)
userC = User("c", "cc", False)
userD = User("d", "dd", False)
userAdmin = User("admin","admin", True)
user_list = [userA, userB, userC, userD, userAdmin]

class Tweet(object):
    def __init__(self, text, hashtags, owner):
        self.text = text
        self.hashtags = hashtags
        self.owner = owner
        #self.read = False

tweet_list = []

def PrintTweet(connection, client_address, tweet):
    connection.sendto("\n~~~~~~~~~~~~~~~~~~~~  NEW POST  ~~~~~~~~~~~~~~~~~~~~", client_address)
    connection.sendto("\nFrom: ", client_address)
    connection.sendto(tweet.owner, client_address)
    connection.sendto("\nPost: ", client_address)
    connection.sendto(tweet.text, client_address)
    connection.sendto("\nTags:", client_address)
    for i in range(len(tweet.hashtags)):
        connection.sendto(" #", client_address)
        connection.sendto(tweet.hashtags[i], client_address)
    connection.sendto("\n~~~~~~~~~~~~~~~~~~~~  END POST  ~~~~~~~~~~~~~~~~~~~~\n\n", client_address)
        

# Returns True if subscription_list (list) has username (string) in it
def isSubscribedTo(subscription_list, username):
    for i in range(len(subscription_list)):
        if subscription_list[i] == username:
            return True
    return False



def UserLogin(connection, client_address):
    connection.sendto("Username: ", client_address)
    username = connection.recv(1000).strip("\r\n")
    connection.sendto("Password: ", client_address)
    password = connection.recv(1000).strip("\r\n")
    for i in range(len(user_list)):
        if user_list[i].username==username and user_list[i].password==password:
            connection.sendto("Welcome, " + user_list[i].username + "\n", client_address)
            user_list[i].online = True;
            user_list[i].connection = connection
            user_list[i].client_address= client_address
            return i
    connection.sendto("Authentication FAILURE\n", client_address)
    return -1

def PrintMainMenu(connection, client_address):
    connection.sendto("Main Menu:\n\nSee Offline Messages (1)\nPost a Message (2)\nAdd a Subscription(3)\nDelete a Subscription(4)\nHashtag Search(5)\nSee Followers(6)\nLogout(7)\n", client_address)
    connection.sendto("You may input ':q!' at any time to quit to the main menu\n", client_address)
            
def SeeOfflineMessages(connection, client_address, cur_user_index):
    connection.sendto("See all messages (1)\nSee messages from a particular subscription (2)\n", client_address)
    command = connection.recv(1000).strip("\r\n")
    if command=="1":
        for i in range(len(user_list[cur_user_index].unread_message_list)):
            PrintTweet(connection, client_address, user_list[cur_user_index].unread_message_list[i])
        del user_list[cur_user_index].unread_message_list[:]
        connection.sendto("No more unread messages\n", client_address)
    elif command=="2":
        connection.sendto("Your current subscriptions are:\n", client_address)
        for i in range(len(user_list[cur_user_index].subscribed_to_list)):
            connection.sendto(user_list[cur_user_index].subscribed_to_list[i], client_address)
            connection.sendto("\n", client_address)
        connection.sendto("Choose a user to see offline messages from: ", client_address)
        user = connection.recv(1000).strip("\r\n")
        if user==":q!":
            return
        messages_found = 0
        # Show messages from specific user
        for i in range(len(user_list[cur_user_index].unread_message_list)):
            if user_list[cur_user_index].unread_message_list[i].owner==user:
                PrintTweet(connection, client_address, user_list[cur_user_index].unread_message_list[i])
                messages_found += 1
        if messages_found==0:
            connection.sendto("Invalid user or No offline messages from this user\n", client_address)
        # Remove messages from specific user
        while messages_found>0:
            for i in range(len(user_list[cur_user_index].unread_message_list)):
                if user_list[cur_user_index].unread_message_list[i].owner==user:
                    (user_list[cur_user_index].unread_message_list).remove(user_list[cur_user_index].unread_message_list[i])
                    messages_found -= 1
                    break
        connection.sendto("\nYou have ", client_address)
        connection.sendto(str(len(user_list[cur_user_index].unread_message_list)), client_address)
        connection.sendto(" unread messages.\n", client_address)
    elif command==":q!":
        return
    else:
        connection.sendto("Invalid command. You have been sent to main menu.\n", client_address)


def NewUser(connection, client_address):
    connection.sendto("New User Creation: \n", client_address)
    connection.sendto("Username: ", client_address)
    username = connection.recv(1000).strip("\r\n")
    if username==":q!":
        return
    connection.sendto("Password: ", client_address)
    password = connection.recv(1000).strip("\r\n")
    if password==":q!":
        return
    new_user = User(username, password, False)
    user_list.append(new_user)
    connection.sendto("New User has been created\n", client_address)


def PostMessage(connection, client_address, cur_user_index):
    owner = user_list[cur_user_index].username
    
    connection.sendto("Public post (1)\nPrivate post(2)\n", client_address)
    command = connection.recv(1000).strip("\r\n")
    private_tweet_flag = False
    if command=="1":
        pass
    elif command=="2":
        private_tweet_flag = True
    elif command==":q!":
        return
    else:
        connection.sendto("Invalid command. You have been sent to main menu\n", client_address)
        return
        
    tweet_txt = ""
    while len(tweet_txt)>140 or tweet_txt=="":
        connection.sendto("Post a tweet (140 chars or less):\n", client_address)
        tweet_txt = connection.recv(1000).strip("\r\n")
        if len(tweet_txt)>140:
            connection.sendto("Tweet too long, try again.\n", client_address)
        elif tweet_txt==":q!":
            connection.sendto("You have quit back to the main menu\n", client_address)
            return
    
    connection.sendto("Add tags to your tweets. Enter input for each tag. Input ':done!' when done inputting tags\n", client_address)
    tweet_hashtag = ""
    tweet_hashtag_list = []
    while tweet_hashtag!=":done!":
        tweet_hashtag = connection.recv(1000).strip("\r\n")
        if tweet_hashtag!=":done!":
            tweet_hashtag_list.append(tweet_hashtag)
        if tweet_hashtag==":q!":
            return
    
    new_tweet = Tweet(tweet_txt, tweet_hashtag_list, owner)
    tweet_list.append(new_tweet)

    if private_tweet_flag==True:
        connection.sendto("\n\nUsers available to private post to:\n", client_address)
        for i in range(len(user_list)):
            connection.sendto(user_list[i].username, client_address)
            connection.sendto("\n", client_address)
        connection.sendto("Input a user to send to: ", client_address)
        user = connection.recv(1000).strip("\r\n")
        if user==":q!":
            return
        found_user_flag = False
        for i in range(len(user_list)):
            if user_list[i].username==user:
                if user_list[i].online==True:
                    PrintTweet(user_list[i].connection, user_list[i].client_address, new_tweet)
                    found_user_flag = True
                    break
                else:
                    user_list[i].unread_message_list.append(new_tweet)
        if found_user_flag==False:
            connection.sendto("Not a valid user. Your post has not been sent.\n", client_address)
            return
    else:
        # Tweet to all people currently online and subscribed to our current user
        # Store in unread message list if offline and subscribed to our current user
        for i in range(len(user_list)):
            if user_list[i].online==True and isSubscribedTo(user_list[i].subscribed_to_list, user_list[cur_user_index].username)==True:
                PrintTweet(user_list[i].connection, user_list[i].client_address, new_tweet)
            elif user_list[i].online==False and isSubscribedTo(user_list[i].subscribed_to_list, user_list[cur_user_index].username)==True:
                user_list[i].unread_message_list.append(new_tweet)
    connection.sendto("Your tweet has been processed\n", client_address)

def AddSubscription(connection, client_address, cur_user_index):
    username = ""
    while username!=":q!":
        connection.sendto("Your current subscriptions are:\n", client_address)
        for i in range(len(user_list[cur_user_index].subscribed_to_list)):
            connection.sendto(user_list[cur_user_index].subscribed_to_list[i], client_address)
            connection.sendto("\n", client_address)
        connection.sendto("\n\nUsers available to subscribe to:\n", client_address)
        for i in range(len(user_list)):
            connection.sendto(user_list[i].username, client_address)
            connection.sendto("\n", client_address)
    
        connection.sendto("\nInput a user to subscribe to: ", client_address)
        username = connection.recv(1000).strip("\r\n")
        if username==":q!":
            return
        add_user_success_flag = False
        for i in range(len(user_list)):
            if username==user_list[i].username:
                for j in range(len(user_list[cur_user_index].subscribed_to_list)):
                    if username==user_list[cur_user_index].subscribed_to_list[j]:
                        user_list[cur_user_index].subscribed_to_list.remove(username)
                        break
                user_list[cur_user_index].subscribed_to_list.append(username)
                connection.sendto("You have added ", client_address)
                connection.sendto(username, client_address)
                connection.sendto(" to your subscription list\n", client_address)
                add_user_success_flag = True
                break
        if add_user_success_flag==False:
            connection.sendto("No such user exists\n", client_address)

def DeleteSubscription(connection, client_address, cur_user_index):
    username = ""
    while username!=":q!":
        connection.sendto("Your current subscriptions are:\n", client_address)
        for i in range(len(user_list[cur_user_index].subscribed_to_list)):
            connection.sendto(user_list[cur_user_index].subscribed_to_list[i], client_address)
            connection.sendto("\n", client_address)
    
        connection.sendto("\nInput a user to unsubscribe from: ", client_address)
        username = connection.recv(1000).strip("\r\n")
        if username==":q!":
            return
        delete_user_success_flag = False
        for i in range(len(user_list)):
            if username==user_list[i].username:
                for j in range(len(user_list[cur_user_index].subscribed_to_list)):
                    if username==user_list[cur_user_index].subscribed_to_list[j]:
                        user_list[cur_user_index].subscribed_to_list.remove(username)
                        connection.sendto("You have unsubscribed from  ", client_address)
                        connection.sendto(username, client_address)
                        connection.sendto("\n", client_address)
                        delete_user_success_flag = True
                        break
        if delete_user_success_flag==False:
            connection.sendto("No such user exists\n", client_address)
    
def HashtagSearch(connection, client_address):
    search_tag = ""
    connection.sendto("Tag to search for: ", client_address)
    search_tag = connection.recv(1000).strip("\r\n")
    if search_tag==":q!":
        return
    
    matches_found = 0
    for i in reversed(tweet_list):
        for j in range(len(i.hashtags)):
            if i.hashtags[j]==search_tag:
                PrintTweet(connection, client_address, i)
                matches_found = matches_found + 1
                if matches_found==10:
                    return

def SeeFollowers(connection, client_address, cur_user_index):
    connection.sendto("Users subscribed to you:\n", client_address)
    for i in range(len(user_list)):
        if isSubscribedTo(user_list[i].subscribed_to_list, user_list[cur_user_index].username)==True:
            connection.sendto(user_list[i].username, client_address)
            connection.sendto("\n", client_address)



def Menu(connection, client_address):
    menu_state = "login"
    
    while True:
        if menu_state=="login":
            cur_user_index = UserLogin(connection, client_address)
            if cur_user_index==-1:
                menu_state = "login"
            else:
                menu_state = "main"
                connection.sendto("\nYou have ", client_address)
                connection.sendto(str(len(user_list[cur_user_index].unread_message_list)), client_address)
                connection.sendto(" unread messages.\n", client_address)
        else: # "main"
            PrintMainMenu(connection, client_address)
            command = connection.recv(1000).strip("\r\n")
            if command=="messagecount" and user_list[cur_user_index].admin==True:
                # "messagecount"
                connection.sendto("\nMessages since server started: ", client_address)
                connection.sendto( str(len(tweet_list)), client_address )
                connection.sendto("\n", client_address)
            elif command=="usercount" and user_list[cur_user_index].admin==True:
                # "usercount"
                connection.sendto("\nNumber of users currently online: ", client_address)
                user_count = 0
                for i in range(len(user_list)):
                    if user_list[i].online==True:
                        user_count += 1
                connection.sendto(str(user_count), client_address)
                connection.sendto("\n", client_address)
            elif command=="storedcount" and user_list[cur_user_index].admin==True:
                # "stored_count"
                stored_count = 0
                for i in range(len(user_list)):
                    stored_count += len(user_list[i].unread_message_list)
                connection.sendto("\nNumber messages stored but not received because the user is offline: ", client_address)
                connection.sendto(str(stored_count), client_address)
                connection.sendto("\n", client_address)
            elif command=="newuser" and user_list[cur_user_index].admin==True:
                # "new_user"
                NewUser(connection, client_address)
            elif command=="1": 
                #"see_offline_messages"
                SeeOfflineMessages(connection, client_address, cur_user_index)                
            elif command=="2": 
                #"post_message"
                PostMessage(connection, client_address, cur_user_index)
            elif command=="3":
                #"add_subscription"
                AddSubscription(connection, client_address, cur_user_index)
            elif command=="4":
                # "delete_subscription"
                DeleteSubscription(connection, client_address, cur_user_index)
            elif command=="5":
                # "hashtag_search
                HashtagSearch(connection, client_address)
            elif command=="6":
                # "see_followers"
                SeeFollowers(connection, client_address, cur_user_index)
            elif command=="7":
                # "logout"
                user_list[cur_user_index].online = False
                user_list[cur_user_index].connection = None
                user_list[cur_user_index].client_address = 0
                del user_list[cur_user_index].unread_message_list[:]
                cur_user_index = -1
                connection.sendto("LOGOUT", client_address)
                return


''' -------------- MAIN CODE -------------- '''
#socket() - Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#bind() -  Bind the socket to the port
server_address = ('',10000)
print >> sys.stderr, 'starting up on %s port %s' %server_address
sock.bind(server_address)

#listen() - Listen for incoming connections
sock.listen(1)

try:
    while True:
        #accept() -  Wait for a connection (will block until a connection comes in)
        # accept() returns a connection (socket), and client_addres (address of client)
        print >> sys.stderr, 'waiting for a connection'
        connection, client_address = sock.accept()
        print >> sys.stderr, 'connection from', client_address
        thread.start_new_thread(Menu,(connection, client_address) )
           
finally:
    # close() - clean up the connection
    # print "closing connection from ", client_address
    connection.close()
