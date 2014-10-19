PCI extractor
===============
The PCI extractor is a combo of <i>grep</i> and <i>lspci</i>. It helps to extract the right information from a <i>lspci</i> verbose.
Tested with Python2.7 and Python3.4.

# Options
    -p --pci keyword1,keyword2,
        Extract pci device which contains keyword1 or keyword2
        and print pci header.
    -l --line keyword1,keyword2,
        Extract pci device which contains keyword1 or keyword2
        and print pci header + line with keyword.
    -w --word keyword1,keyword2,
        Extract pci device which contains keyword1 or keyword2
        and print pci header + keyword and the next word/value.
    -M --mute-pci
        Mute pci header print
    -m --mute-line
        Mute pci line print
    -s --mute-word
        Mute pci word print
    -r --raw
        Remove extra format char (\t) and print layout
    -h -? --help
        Display the help screen

# Use

## Example of the standard <i>lspci</i> command
```
    $> lspci -vvv
    00:1d.0 USB Controller: Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller
            Subsystem: Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller
            Control: I/O- Mem+ BusMaster+ SpecCycle- MemWINV- VGASnoop- ParErr- Stepping- SERR- FastB2B- DisINTx-
            Status: Cap+ 66MHz- UDF- FastB2B+ ParErr- DEVSEL=medium >TAbort- <TAbort- <MAbort- >SERR- <PERR- INTx-
            Latency: 0
            Interrupt: pin A routed to IRQ 23
            Region 0: Memory at c4904000 (32-bit, non-prefetchable) [size=1K]
            Capabilities: [50] Power Management version 2
                    Flags: PMEClk- DSI- D1- D2- AuxCurrent=375mA PME(D0+,D1-,D2-,D3hot+,D3cold+)
                    Status: D0 NoSoftRst- PME-Enable- DSel=0 DScale=0 PME-
            Capabilities: [58] Debug port: BAR=1 offset=00a0
            Capabilities: [98] PCI Advanced Features
                    AFCap: TP+ FLR+
                    AFCtrl: FLR-
                    AFStatus: TP-

    02:03.0 USB controller: VMware USB2 EHCI Controller (prog-if 20 [EHCI])
            Subsystem: VMware USB2 EHCI Controller
            Physical Slot: 35
            Control: I/O- Mem+ BusMaster+ SpecCycle- MemWINV- VGASnoop- ParErr- Stepping- SERR- FastB2B- DisINTx-
            Status: Cap- 66MHz- UDF- FastB2B- ParErr- DEVSEL=fast >TAbort- <TAbort- <MAbort- >SERR- <PERR- INTx-
            Latency: 64 (1500ns min, 63750ns max)
            Interrupt: pin A routed to IRQ 17
            Region 0: Memory at fd5ff000 (32-bit, non-prefetchable) [size=4K]
            Kernel driver in use: ehci-pci
```

## Standard use
By default, the script calls the <i>lspci</i> command of the system.
```
    $> ./pci-extractor.py -p USB
    00:1d.0 | USB Controller | Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller
    02:03.0 | USB controller | VMware USB2 EHCI Controller

    $> ./pci-extractor.py -l DSel
    00:1d.0 | USB Controller | Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller
        Status: D0 NoSoftRst- PME-Enable- DSel=0 DScale=0 PME-
    02:03.0 | USB controller | VMware USB2 EHCI Controller

    $> ./pci-extractor.py -l DSel -p Intel
    00:1d.0 | USB Controller | Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller
        Status: D0 NoSoftRst- PME-Enable- DSel=0 DScale=0 PME-

    $> ./pci-extractor.py -l DSel -p Intel -m
    00:1d.0 | USB Controller | Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller

    $> ./pci-extractor.py -w DSel
    00:1d.0 | USB Controller | Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller
        DSel 0
    02:03.0 | USB controller | VMware USB2 EHCI Controller

    $> ./pci-extractor.py -w DSel -p Intel
    00:1d.0 | USB Controller | Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller
        DSel 0

    $> ./pci-extractor.py -w DSel -p Intel -M
        DSel 0

    $> ./pci-extractor.py -w DSel -p Intel -M -r
    0
```

## Stdin use
If you have a dump of the <i>lspci</i> command with verbose, you can use the script as well.
```
    $> cat file_with_lspci-vvv.txt | ./pci-extractor.py
    00:1d.0 | USB Controller | Intel Corporation 6 Series/C200 Series Chipset Family USB Enhanced Host Controller
    02:03.0 | USB controller | VMware USB2 EHCI Controller
```