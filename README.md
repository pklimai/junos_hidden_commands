## Searching for all hidden Junos commands

As you may know, Junos OS CLI has some “hidden” commands that are not seen in the context-sensitive help and need to be typed in full. The most well known (and useless) command of such kind is `show version and haiku`, which gives you a 3-line poetry masterpiece every time you enter it.

There is a rather large number of hidden commands, however they are undocumented and good work of your equipment is not guaranteed if you use them. Anyway, sometimes you want to get a complete list (starting from some initial command branch).

Here I present a script that does exactly this.

The idea is very simple. Consider, for example, `show version` command. If we enter `show version a` (press Enter at the end), we get the following output:
```
lab@jsrxA-1> show version a
                           ^
syntax error.
```
On the other hand, for `show version с`, we get
```
lab@jsrxA-1> show version c   
                          ^
syntax error, expecting <command>.
```
In the first case we have a hidden continuation (`and haiku`), in the second one – no. It is seen that in case of a hidden continuation, CLI reacts differently in two aspects:

* “syntax error.” instead of  “syntax error, expecting ‹command›.”;
* hat (a.k.a. circumflex) is under the next position in a line.

So, typing letters one at a time, we can search for hidden commands. A good task for an automation script! 

#### Warning

Note that we will be going through all possible sorts of commands automatically, so never run something like this script in production. Better use a virtual SRX device (a.k.a. Firefly Perimeter) which you can easily recover from a snapshot!

This task will use a direct telnet connection to the device and parse CLI text output (do "screen scraping"), because XML API is not helpful for hidden command search. For most other “automation” tasks, you will use NETCONF API or libraries like Junos PyEZ.

We will only do op mode hidden command search here. Searching for hidden configuration knobs can be, however, performed in a similar manner.

#### Algorithm

So, starting from a particular command (`commandStart in script`) we will walk all possible commands by adding one character at a time (from `alphabet` array) and typing Enter. Junos CLI output can be as follows:

1)	“syntax error.” (and the hat shows that a command has a continuation) — we are processing a hidden-command, proceeding by adding new characters.

2)	“syntax error, expecting ‹command›.” — here we need to analyze the position of a hat. If it is under current character, as we have above in example with `show version c`, then no hidden commands start from these letter, break the cycle.
However if hat is under the next letter, as here:
```
lab@jsrxA-1> show version and 
                              ^
syntax error, expecting <command>.
```
then the command is continued and we need to walk it further (at this point the command can be hidden or not depending on the history).

3)	Usual output, with no syntax errors, but may be with errors about ambiguous input, for example:
```
lab@jlab-Firefly-3> show chassis cluster i
                                          ^
'i' is ambiguous.
Possible completions:
  interfaces           Display chassis cluster interfaces
  ip-monitoring        Display IP monitoring related information
```
In this case we need to continue to recursively walk the command tree, because a hidden command can be present further (in this case, “show chassis cluster information” is hidden).

Also one needs to take into account that outputs of some commands may take several screens and give a “---(more)---“ prompt. In this case we just send a Spacebar (having second thoughts, it could have been achieved with `set cli screen-length 0` as well).


####Examples of output:

Run for `commandStart = “show version “`:
```
hidden command >> show version and (incomplete)
hidden command >> show version and blame
hidden command >> show version and haiku
hidden command >> show version extensive
hidden command >> show version forwarding-context
hidden command >> show version invoke-on (incomplete)
hidden command >> show version invoke-on a
hidden command >> show version invoke-on o
hidden command >> show version no-forwarding
hidden command >> show version scc-dont-forward
hidden command >> show version sdk
```
Run for `commandStart = “show chassis “`:
```
hidden command >> show chassis accurate-statistics
hidden command >> show chassis beacon
hidden command >> show chassis broadcom
hidden command >> show chassis cfeb
hidden command >> show chassis cip
hidden command >> show chassis clocks
hidden command >> show chassis cluster ethernet-switching (incomplete)
hidden command >> show chassis cluster information
hidden command >> show chassis cluster ip-monitoring (incomplete)
hidden command >> show chassis craft-interface
hidden command >> show chassis customer-id
hidden command >> show chassis ethernet-switch
hidden command >> show chassis fabric (incomplete)
hidden command >> show chassis fchip
hidden command >> show chassis feb
hidden command >> show chassis fpc-feb-connectivity
hidden command >> show chassis hsl (incomplete)
hidden command >> show chassis hsr
hidden command >> show chassis hss (incomplete)
hidden command >> show chassis hst
hidden command >> show chassis in-service-upgrade
hidden command >> show chassis ioc-npc-connectivity
hidden command >> show chassis lccs
hidden command >> show chassis message-statistics (incomplete)
hidden command >> show chassis message-statistics i
hidden command >> show chassis network-services
hidden command >> show chassis nonstop-upgrade
hidden command >> show chassis power-budget-statistics
hidden command >> show chassis psd
hidden command >> show chassis redundancy (incomplete)
hidden command >> show chassis redundant-power-system
hidden command >> show chassis scb
hidden command >> show chassis sfm
hidden command >> show chassis sibs
hidden command >> show chassis spmb
hidden command >> show chassis ssb
hidden command >> show chassis synchronization
hidden command >> show chassis tfeb
hidden command >> show chassis timers
hidden command >> show chassis usb (incomplete)
hidden command >> show chassis zones
```

Run for `commandStart = “show security idp “` (on SRX240):
```
hidden command >> show security idp active-policy
hidden command >> show security idp application-ddos (incomplete)
hidden command >> show security idp application-identification (incomplete)
hidden command >> show security idp detector (incomplete)
hidden command >> show security idp detector a
hidden command >> show security idp detector c
hidden command >> show security idp detector p
hidden command >> show security idp ips-cache
hidden command >> show security idp logical-system (incomplete)
```

As seen, some commands are marked as incomplete. These are ones that assume continuation. In case when the continuation of the command is not hidden (once you type the hidden part), such command is typed by a script in a short form (`show chassis message-statistics i` is actually `show chassis message-statistics ipc`).

I was not trying to catch all possible exceptions in this script so you can break its work by, for example, logging to a terminal. I will be glad if you improve it.

Another problem is due to commands that take any name as an entry – for example, `show interfaces AnyInterfaceNameIsOKHere` (in the absence of such interface you get a CLI error, other similar commands may give empty output). That’s why having `show interfaces` as an initial command you will get “maximum recursion depth exceeded” error. However `commandStart = “show interfaces ge-0/0/0”` works fine:

Run for `commandStart = “ge-0/0/0”`:
```
hidden command >> show interfaces ge-0/0/0 forwarding-context
hidden command >> show interfaces ge-0/0/0 ifd-index
hidden command >> show interfaces ge-0/0/0 ifl-index
hidden command >> show interfaces ge-0/0/0 instance
hidden command >> show interfaces ge-0/0/0 no-forwarding
hidden command >> show interfaces ge-0/0/0 scc-dont-forward
```

#### Final notes

Most of hidden commands were hidden because they are not supported (or have no sense) on the particular equipment (or OS version). Many of them are useless, however some may be valuable. Remember, you use them (and the present script) at your own risk. 







