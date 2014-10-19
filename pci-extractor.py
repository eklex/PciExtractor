#!/usr/bin/env python

"""pci-extractor.py: extract data from lspci -vvv command."""

__author__ = "Alexandre Boni"
__copyright__ = "Copyleft 2014, Alexandre Boni"
__credits__ = ["Alexandre Boni"]
__license__ = "CC BY 4.0"
__version__ = "1.0"
__maintainer__ = "Alexandre Boni"
__email__ = ""
__status__ = "Production"

helpString = "\
\n\
\n\
####################\n\
### Option flags ###\n\
####################\n\
\n\
    -p --pci keyword1,keyword2,\n\
        Extract pci device which contains keyword1 or keyword2\n\
        and print pci header.\n\
    -l --line keyword1,keyword2,\n\
        Extract pci device which contains keyword1 or keyword2\n\
        and print pci header + line with keyword.\n\
    -w --word keyword1,keyword2,\n\
        Extract pci device which contains keyword1 or keyword2\n\
        and print pci header + keyword and the next word/value.\n\
    -M --mute-pci\n\
        Mute pci header print\n\
    -m --mute-line\n\
        Mute pci line print\n\
    -s --mute-word\n\
        Mute pci word print\n\
    -r --raw\n\
        Remove extra format char (\\t) and print layout\n\
    -h -? --help\n\
        Display this help\n\
\n\
\n\
####################\n\
###   Examples   ###\n\
####################\n\
    Note: To simplify examples, the PCI tree has only the devices below.\n\
\n\
    $> lspci -vvv\n\
    00:1d.0 USB Controller: Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller\n\
            Subsystem: Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller\n\
            Control: I/O- Mem+ BusMaster+ SpecCycle- MemWINV- VGASnoop- ParErr- Stepping- SERR- FastB2B- DisINTx-\n\
            Status: Cap+ 66MHz- UDF- FastB2B+ ParErr- DEVSEL=medium >TAbort- <TAbort- <MAbort- >SERR- <PERR- INTx-\n\
            Latency: 0\n\
            Interrupt: pin A routed to IRQ 23\n\
            Region 0: Memory at c4904000 (32-bit, non-prefetchable) [size=1K]\n\
            Capabilities: [50] Power Management version 2\n\
                    Flags: PMEClk- DSI- D1- D2- AuxCurrent=375mA PME(D0+,D1-,D2-,D3hot+,D3cold+)\n\
                    Status: D0 NoSoftRst- PME-Enable- DSel=0 DScale=0 PME-\n\
            Capabilities: [58] Debug port: BAR=1 offset=00a0\n\
            Capabilities: [98] PCI Advanced Features\n\
                    AFCap: TP+ FLR+\n\
                    AFCtrl: FLR-\n\
                    AFStatus: TP-\n\
\n\
    02:03.0 USB controller: VMware USB2 EHCI Controller (prog-if 20 [EHCI])\n\
            Subsystem: VMware USB2 EHCI Controller\n\
            Physical Slot: 35\n\
            Control: I/O- Mem+ BusMaster+ SpecCycle- MemWINV- VGASnoop- ParErr- Stepping- SERR- FastB2B- DisINTx-\n\
            Status: Cap- 66MHz- UDF- FastB2B- ParErr- DEVSEL=fast >TAbort- <TAbort- <MAbort- >SERR- <PERR- INTx-\n\
            Latency: 64 (1500ns min, 63750ns max)\n\
            Interrupt: pin A routed to IRQ 17\n\
            Region 0: Memory at fd5ff000 (32-bit, non-prefetchable) [size=4K]\n\
            Kernel driver in use: ehci-pci\n\
\n\
\n\
  ####################\n\
  ### Standard use ###\n\
  ####################\n\
\n\
    $> ./pci-extractor.py -p USB\n\
    00:1d.0 | USB Controller | Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller\n\
    02:03.0 | USB controller | VMware USB2 EHCI Controller\n\
    \n\
    $> ./pci-extractor.py -l DSel\n\
    00:1d.0 | USB Controller | Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller\n\
        Status: D0 NoSoftRst- PME-Enable- DSel=0 DScale=0 PME-\n\
    02:03.0 | USB controller | VMware USB2 EHCI Controller\n\
    \n\
    $> ./pci-extractor.py -l DSel -p Intel\n\
    00:1d.0 | USB Controller | Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller\n\
        Status: D0 NoSoftRst- PME-Enable- DSel=0 DScale=0 PME-\n\
    \n\
    $> ./pci-extractor.py -l DSel -p Intel -m\n\
    00:1d.0 | USB Controller | Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller\n\
    \n\
    $> ./pci-extractor.py -w DSel\n\
    00:1d.0 | USB Controller | Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller\n\
        DSel 0\n\
    02:03.0 | USB controller | VMware USB2 EHCI Controller\n\
    \n\
    $> ./pci-extractor.py -w DSel -p Intel\n\
    00:1d.0 | USB Controller | Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller\n\
        DSel 0\n\
    \n\
    $> ./pci-extractor.py -w DSel -p Intel -M\n\
        DSel 0\n\
    \n\
    $> ./pci-extractor.py -w DSel -p Intel -M -r\n\
    0\n\
\n\
\n\
  ####################\n\
  ###  Stdin feat. ###\n\
  ####################\n\
\n\
    $> cat file_with_lspci-vvv.txt | ./pci-extractor.py\n\
    00:1d.0 | USB Controller | Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller\n\
    02:03.0 | USB controller | VMware USB2 EHCI Controller\n\
    \n\
\n\
"

import os
import sys
import getopt
import select
import subprocess
import re

def removeOption(name):
    """removeOption: Remove string between [], {}, ()."""
    tmpStr = ""
    bracket = 0
    if not name:
        return None
    for i in range(0,len(name)):
        if name[i] in ("(","[","{"):
            bracket += 1
        elif name[i] in ("]",")","}"):
            bracket -= 1
        elif bracket == 0:
            tmpStr += name[i]
    return tmpStr

def getId(pciDev):
    """getId: Get the bus:device:function string."""
    if not pciDev:
        return None
    if isinstance(pciDev, str):
        pciId = pciDev.split(" ")
    elif isinstance(pciDev, list):
        pciId = pciDev[0].split(" ")
    if pciId[0]:
        return pciId[0]
    return None

def getType(pciDev):
    """getType: Get the PCI device type."""
    pciType = ""
    if not pciDev:
        return None
    if isinstance(pciDev, str):
        pciId = pciDev.split(" ")
    elif isinstance(pciDev, list):
        pciId = pciDev[0].split(" ")
    if pciId[0]:
        for i in range(1,len(pciId)):
            pciType += pciId[i] + " "
            if pciType[-2] == ":":
                pciType = pciType[:-2]
                break
        return pciType.strip()
    return None

def getName(pciDev, wOption=False):
    """getName: Get the PCI device name."""
    pciName = ""
    if not pciDev:
        return None
    if isinstance(pciDev, str):
        pciId = pciDev.split(": ")
    elif isinstance(pciDev, list):
        pciId = pciDev[0].split(": ")
    if pciId[0] and pciId[1]:
        pciName = pciId[1].split("\n")[0]
        if not wOption:
            pciName = removeOption(pciName)
        return pciName.strip()
    return None

def getLine(pciDev, keyword, wOption=True):
    """getLine: Get list of line where keyword is found."""
    pciLine = []
    if not keyword or not pciDev:
        return None
    if isinstance(pciDev, str):
        pciDev = pciDev.split("\n")
    for line in pciDev:
        if keyword in line:
            if not wOption and pciLine:
                line = removeOption(line)
            pciLine.append(line)
    if pciLine != ['']:
        return pciLine
    return None

def getInline(line, keyword, wOption=True):
    """getInline: Get the word after the keyword in line.
    i.e.:   line="Speed 5GT/s, Width x4", keyword="Speed"
            return "5GT/s"
    """
    linelist = []
    if not line or not keyword:
        return None
    tmplist = re.split(" |;|,|=|:|\n", line)
    for item in tmplist:
        if item:
            linelist.append(item)
    for i, item in enumerate(linelist):
        if keyword in item and i+1<len(linelist):
            return linelist[i+1]
    return None

def lspciData():
    """lspciData: Get file contents or lspci verbose output."""
    output = None
    try:
        output = select.select([sys.stdin], [], [], 0)[0]
    except:
        pass
    if output and output[0] == sys.stdin:
        output = output[0].read()
    else:
        try:
            output = subprocess.check_output(["lspci -vvv"], shell=True)
        except:
            print("lspci command failed!!!")
            sys.exit(1)
    return output
    
def processOption(argv):
    """processOption: Process options parsed by command line."""
    optionDict = {
        "pci-keyword" : "",
        "line-keyword" : "",
        "inline-keyword" : "",
        "mute-pci" : False,
        "mute-line" : False,
        "mute-inline" : False,
        "raw-print" : False,
    }
    try:
        opts, args = getopt.getopt(argv[1:], \
                                   "p:l:w:Mmsh?r", \
                                   ["pci=", "line=", "word=", \
                                    "mute-pci", "mute-line", "mute-word" \
                                    "raw", "help"])
    except getopt.GetoptError as err:
        print(err)
        return None
    for op, ar in opts:
        if op in ("-h", "-?", "--help"):
            print(helpString)
            pass
            sys.exit(1)
        elif op in ("-p", "--pci"):
            optionDict["pci-keyword"] = ar
            pass
        elif op in ("-l", "--line"):
            optionDict["line-keyword"] = ar
            pass
        elif op in ("-w", "--word"):
            optionDict["inline-keyword"] = ar
            pass
        elif op in ("-M", "--mute-pci"):
            optionDict["mute-pci"] = True
            pass
        elif op in ("-m", "--mute-line"):
            optionDict["mute-line"] = True
            pass
        elif op in ("-s", "--mute-word"):
            optionDict["mute-inline"] = True
            pass
        elif op in ("-r", "--raw"):
            optionDict["raw-print"] = True
            pass
        else:
            raise(False,"unsupported option")
    return optionDict
    
if __name__ == "__main__":
    # initialize lists
    sortedPciDevice = []
    sortedPciLine = []
    sortedPciInline = []
    
    # retrieve options
    option = processOption(sys.argv)

    # process keywords
    pcidev_keyword = option["pci-keyword"].split(",")
    line_keyword = option["line-keyword"].split(",")
    inline_keyword = option["inline-keyword"].split(",")
    
    # not line keyword available
    # then inline and line keywords are the same
    if not option["line-keyword"]:
        line_keyword = inline_keyword
    # retrieve data
    lspciv = lspciData()
    if not lspciv:
        print("invalid lspci data")
        sys.exit(1)
    # format data
    lspciv = lspciv.replace("\t","") # remove tab
    lspciv = lspciv.split("\n\n")    # split by pci device
    
    """
    # Extract relevant device in lspci list.
    """
    # pci keyword not empty,
    # then extract pci dev by pci keyword
    if option["pci-keyword"]:
        # run through each pci device
        for pcidev in lspciv:
            # run through each pci keyword
            for pcikey in pcidev_keyword:
                # if keyword not null and found in pci device
                if pcikey and pcikey in pcidev:
                    # create list of pci lines
                    pcidev = pcidev.split('\n')
                    # add to the pci dev list
                    sortedPciDevice.append(pcidev)
    # no pci keyword,
    # then take every pci device
    else:
        sortedPciDevice = lspciv
    """
    " Extract relevant lines in pci device list.
    """
    # if line keyword list not empty,
    # sort by line keyword
    if line_keyword != ['']:
        for pcidev in sortedPciDevice:
            pciline = []
            # run through each line keyword
            for linekey in line_keyword:
                # if keyword not null
                if linekey:
                    # search line keyword in pci line
                    tmpline = getLine(pcidev, linekey, False)
                    # if keyword found then add result
                    if tmpline:
                        pciline += tmpline
            # results were found
            if pciline:
                # lines found not null, split into a list
                #pciline = pciline.split("\n")
                pass
            # save it to the pci line list
            # even if the result is null
            sortedPciLine.append(pciline)
            
    """
    " Extract relevant word in pci line list.
    """
    # if the inline keyword list not empty
    # and pci line list not empty
    if inline_keyword != [''] and sortedPciLine:
        for pciline in sortedPciLine:
            pciinlinelist = []
            for subpciline in pciline:
                for inlinekey in inline_keyword:
                    if inlinekey:
                        pciinline = getInline(subpciline, inlinekey)
                        if pciinline:
                            pciinlinelist.append((inlinekey,pciinline))
            sortedPciInline.append(pciinlinelist)
    
    """
    " Print generated lists.
    """
    for i, pcidev in enumerate(sortedPciDevice):
        if not pcidev:
            continue
        if not option["mute-pci"]:
            print(getId(pcidev)+" | "+getType(pcidev)+" | "+getName(pcidev))
        if option["line-keyword"] and sortedPciLine[i] and not option["mute-line"]:
            for item in sortedPciLine[i]:
                if option["raw-print"]:
                    print(item)
                else:
                    print("\t%s"%item)
        if option["inline-keyword"] and sortedPciInline[i] and not option["mute-inline"]:
            for item in sortedPciInline[i]:
                if option["raw-print"]:
                    print(item[1])
                else:
                    print("\t%s %s"%(item[0],item[1]))
    
