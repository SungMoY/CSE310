# analyze a PCAP file to characterize TCP flows in trace

import dpkt

# These were allowed to be hardcoded as per the homework pdf
# otherwise, import sockets as use .inet_ntoa() to decode
# ip.src and ip.dst into IP addresses
senderIP = '130.245.145.12'
receiverIP = '128.208.2.198'

f = open('assignment2.pcap', 'rb')
pcap = dpkt.pcap.Reader(f)

numOfFlowsInitatedFromSender = 0

flowDict = {}
for ts, buf in pcap:
    eth = dpkt.ethernet.Ethernet(buf)
    ip = eth.data
    # check if packet is a TCP packet
    if ip.p == dpkt.ip.IP_PROTO_TCP:
        tcp = ip.data

        # check for dpkt.tcp.TH_FIN flag
        # if tcp.flags & dpkt.tcp.TH_FIN:
        #     print("FIN flag found")

        # store each flow in a dictionary
        # the key is a tuple of sender port and receiver port
        # the value is a list of all interactions between the sender and the receiver

        currentTuple = (tcp.sport, tcp.dport)
        # current Tuple could be either 4xxxxx, 80 or 80, 4xxxxx. these should point to the same dict entry
        otherValidTuple = (tcp.dport, tcp.sport)
        # it is guaranteed that the start of each flow is from the sender, so the key will always be 4xxxxx, 80

        if currentTuple in flowDict:
            # working on existing TCP flow - current packet is from sender
            flowDict[currentTuple].append([tcp, senderIP, ts])
        elif otherValidTuple in flowDict:
            # working on existing TCP flow - current packet is from receiver - THIS IS STILL THE SAME FLOW
            flowDict[otherValidTuple].append([tcp, receiverIP, ts])
        else: 
            # new TCP flow initiated
            flowDict[currentTuple] = [[tcp, senderIP, ts]]

f.close()

printString = "\nNumber of TCP flows initiated from sender: "+ str(len(flowDict.keys()))+  "\n\nTCP Flows:\n"
flowNum = 1
for flow in flowDict:
    numOfFlowsInitatedFromSender += 1
    # currentTCPFlow is an array of packets in this specific flow
    currentTCPFlow = flowDict[flow]
    # retrieve data from the first packet in the flow
    # this is okay because the first packet is guaranteed to be from the sender
    currentTCP = currentTCPFlow[0][0]
    currentTheirIP = currentTCPFlow[0][1]

    # necessary data points for each packet: 
    # currentTCP.sport, currentTCP.dport, currentTCP.seq, currentTCP.ack, currentTCP.win, currentTCP.data

    printString += "[Flow "+str(flowNum)+"]"+ "\t(source port: "+ str(currentTCP.sport)+", source IP: "+ str(currentTheirIP)+", destination port: "+ str(currentTCP.dport)+", destination IP: "+ str(receiverIP)+")\n"
    printString += "\t\t\tTransactions:\n"
    flowNum += 1
    

    firstTimestamp = 0
    firstTimestampBool = True
    lastTimestamp = 0

    # firstTimestamp is recorded when the first byte of data is sent
    if firstTimestampBool and len(tcp.data) > 0:
        firstTimestamp = ts
        firstTimestampBool = False


    firstTwoTransactions = []
    firstTwoTransactionsDoneBool = False
    byteCount = 0

    for packet in currentTCPFlow:
        currentTCP = packet[0]
        currentSenderIP = packet[1]
        currentTimeStamp = packet[2]

        # measuring total amount of data sent by number of bytes of the entire packet (including headers, data, etc)
        byteCount += len(currentTCP)

        #firstTimestamp is at the very first packet of each flow
        if firstTimestampBool:
            firstTimestamp = currentTimeStamp
            firstTimestampBool = False
        # lastTimestamp is at the very last packet of each flow so keep updating it at each packet
        lastTimestamp = currentTimeStamp

        # if currentTCP.flags & dpkt.tcp.TH_FIN:
        #     print("\t\t\tFIN")

        if len(firstTwoTransactions) < 2 and len(currentTCP.data) > 0 and currentSenderIP == senderIP and not firstTwoTransactionsDoneBool:
            firstTwoTransactions.append(currentTCP)
            printString += "\t\t\t\tSEQ: "+ str(currentTCP.seq)+"\t\tACK: "+ str(currentTCP.ack)+"\t\tWIN: "+ str(currentTCP.win)+"\n"
        elif len(firstTwoTransactions) > 0 and currentSenderIP == receiverIP:
            if len(firstTwoTransactions[0].data) + firstTwoTransactions[0].seq == currentTCP.ack:
                firstTwoTransactions.pop(0)
                printString += "\t\t\t\tSEQ: "+ str(currentTCP.seq)+"\t\tACK: "+ str(currentTCP.ack)+"\t\tWIN: "+ str(currentTCP.win)+"\n"
            if len(firstTwoTransactions) > 1 and currentSenderIP == receiverIP:
                if len(firstTwoTransactions[1].data) + firstTwoTransactions[1].seq == currentTCP.ack:
                    firstTwoTransactions.pop(1)
                    printString += "\t\t\t\tSEQ: "+ str(currentTCP.seq)+"\t\tACK: "+ str(currentTCP.ack)+"\t\tWIN: "+ str(currentTCP.win)+"\n"
        if len(firstTwoTransactions) == 2:
            firstTwoTransactionsDoneBool = True

    printString += "\t\t\tThroughput: "+ str(byteCount/(lastTimestamp - firstTimestamp)) +" bytes/sec\n"
    printString += "\t\t\tCongestion window sizes: "

    currentCongestionWindow = []
    numOfCongestionWindows = 0
    for packet in currentTCPFlow[3:]:
        currentTCP = packet[0]
        currentSenderIP = packet[1]
        currentTimeStamp = packet[2]

        if currentTCP.sport != 80:
            # append to the array the value of the ACK that the reciever must send
            currentCongestionWindow.append(currentTCP.seq + len(currentTCP.data))
        else:
            if len(currentCongestionWindow) > 0:
                if currentCongestionWindow[0] == currentTCP.ack:
                    printString += str(len(currentCongestionWindow))+", "
                    currentCongestionWindow = []
                    numOfCongestionWindows += 1

        if numOfCongestionWindows == 3:
            printString = printString[:-2]
            printString += "\n"
            break

    packetsFromReceiver = []
    retransmitTripleDupeACKLibrary = []
    retransmissionTripleDupeACKCount = 0
    for packet in currentTCPFlow:
        currentTCP = packet[0]
        if currentTCP.sport == 80:
            packetsFromReceiver.append(currentTCP)
    for x in range(len(packetsFromReceiver)-2):
        firstPack = packetsFromReceiver[x]
        secondPack = packetsFromReceiver[x+1]
        thirdPack = packetsFromReceiver[x+2]
        if firstPack.ack == secondPack.ack and firstPack.ack == thirdPack.ack:
            if firstPack.seq == secondPack.seq and firstPack.seq == thirdPack.seq:
                if firstPack.ack not in retransmitTripleDupeACKLibrary:
                    retransmitTripleDupeACKLibrary.append(firstPack.ack)
                    retransmissionTripleDupeACKCount += 1

    printString += "\t\t\tRetransmissions due to triple duplicate ACK: "+ str(retransmissionTripleDupeACKCount) +"\n"

    packetsFromSender = []
    retransTotal = 0
    for packet in currentTCPFlow:
        currentTCP = packet[0]
        if currentTCP.sport != 80:
            packetsFromSender.append(currentTCP.seq)
    for packetSEQ in packetsFromSender:
        if packetsFromSender.count(packetSEQ) > 1:
            retransTotal += 1


    printString += "\t\t\tRetransmissions due to timeout: "+ str(retransTotal - retransmissionTripleDupeACKCount) +"\n"

    #break
    #break to only go through first flow

print(printString+"\n")

