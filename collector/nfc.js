var NetFlowCollection = function () {
    
    var self = this;
    
    self.flows = 0;
    self.bytesCount = 0;
    self.packetsCount = 0;
    self.protocols = {
        TCP: 0,
        ICMP: 0,
        Telnet: 0,
        UDP: 0,
    };
    
    self.uniquePairs = {};
    self.bytesArray = [];
    
    self.addrList = [];

    self.add = function (flow) {
        
        self.bytesCount += flow.bytesCount;
        self.packetsCount += flow.packetsCount;
        
        self.protocols.TCP += flow.protocols.TCP;
        self.protocols.ICMP += flow.protocols.ICMP;
        self.protocols.Telnet += flow.protocols.Telnet;
        self.protocols.UDP += flow.protocols.UDP;
        
        for (var p in flow.uniquePairs) {
            self.uniquePairs[p] = 1;
        }
        
    };
    
    self.uniquePairsCount = 0;
    
    self.inline = function (time) {
        self.uniquePairsCount = Object.keys(self.uniquePairs).length;
        console.log("[" + new Date(time) + "]\n" + self.uniquePairsCount + "," + self.bytesCount + "," + self.packetsCount);
        return time + "," + self.uniquePairsCount + "," + self.bytesCount + "," + self.packetsCount;
    }
    
};


exports.NetFlowCollection = NetFlowCollection;