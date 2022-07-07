# LTZ-Chain
```python
                   %%%%%.%                              
                %%%% %%%%%%%%%%                                                                   
           %%%%%%%%%%%%%%%%%%%%%%%%,                                                              
       %%%%%%%%%%%%%% %#%%%%%%%%%%#%%%%%                                                          
   %%%%%%%%%%%%%%%%% %%%% %%%%%%% %%%%%%%%%%                                                      
 %%%%%%%%%%%%%%%%%% %%%%%%% %%%% %%%%%%%%%%%%% 
  %%%%%%%%%%%%%%%%,%%%%%%%%%%. %%%%%%%%%%%%%%% 
 %% %%%%%%%%%%%%%%%%%%%%%%%%%  %%%%%%%%%%%%%%% 
 %%%% %%%%%%%%% %%%%%%%%%%%%,%%% %%%%%%%%%%%%% 
 %%%%%% %%%%%% %%%%%%%%%%% %%%%%%% %%%%%%%%%%% 
 %%%%%%%% %%% %%%%%%%%%%% %%%%%%%%%#%%%%%%%%%% 
 %%%%%%%%%%  %%%%%%%%%%%%%%%%%%%%%%%% %%%%%%%  
 %%%%%%%%%%/% %%%%%%%% %%%%%%%%%%%%%%%% %%%%,%  
 %%%%%%%%#%%%%% %%%%% %%%%%%%%%%%%%%%%%%%. %%% 
 %%%%%%% %%%%%%%% %#%%%%%%%%%%%%%%%%%%%%%  %%% 
 %%%%%% %%%%%%%%%% .%%%%%%%%%%%%%%%%%%%%%%%% % 
     % %%%%%%%%%% %%%/%%%%%%%%%%%%%%%% %%%    
         %%%%%%.%%%%%%%##%%%%%%%%%%%%         
             / %%%%%%%%%%%,%%%%%%            
                  %%%%%%%%%%                
                     %%%                                     
```

World's first fully decentralized light-weight multi-purpose python based blockchain with top-notch security features.

## Current Features & Updates 🎉
1. A tradeable and exchangeable **native chain currency** with the ticker **LTZ** which will be used for paying miners and for other upcoming events and projects.
2. Support for **link based storage** and **plain text storage** as coinbase field. (although can only be issued by successful block miners.)
3. Securing transactions and lumps with digital signatures with 1024 bits keypairs to ensure there is no tampering with data.
4. UTXO-DB for allowing lumped transactions making sure tokens can be sent or received in smaller changes.
5. Secure syncing and verification methods to prevent foul blocks from being generated.
6. **Allowing forking and multiple branches** for different blockchain based projects to parallelly use.
7. Calculating branches with the most efficiency and very less disk and ram usage with the estimates of **max peak of A few hundred megabytes of ram usage at 1 million blocks**.
8. Multiple lumps per block supported with a **max block size limit of 1 megabyte**.(usually 100 lumps ber block at max but any number allowed as long as it does not go above the block limit)
9. Extra coinbase field in which block-miner can store text or link pointing at NFTS making sure they remain permanent and untampered on the blockchain.
10. All types of issues like bazantine's generals problem or longest chain rule etc. have been implemented to make sure that there is no way to exploit the chain or tamper any data.
11. **CPU based PoW mining** (subject to changes) and reward of 1 LTZ per block mined.(mining empty blocks are also permitted on the network for a short time)
12. Everything precompiled in .pyc file formats to speed-up CPU-based processing. You can also git clone .py files from the repo and use those instead if you wish to.
13. **No external dependencies have been used into making this project therefore eliminating the frustration of installing libraries.**
14. People connected in the network can also send messages on the network which can be seen by everyone on the network replicating the behaviour of a p2p chat application at the same time cause why not? (although this feature will most probably be removed soon in further versions).
15. Messages are now also mined with a really small target averaging around 2 seconds per message on a dual core cpu. This has been done to prevent message spamming and DDoS Attacks.

Read more at https://aaravdayal.com/

## Installation
```bash
git clone https://github.com/Lumatozer/LTZ-Chain/build ltz
```
## Initialization
1. Start the node
```python
python node.py {port number}(optional)
BlockChain -> {
  Your host port is {your_host_port}
}
Node >>                                                                                                                                                                                                                                                                                                                                                                                                                                         
```
You have now started the node.

2. Next connect to a peer on the network which you know of.\
 (Now there will be automatic sync sequence.
Please wait until syncing is complete.)
```bash
Node >> add
~~-Add-New-Peer-~~
I.P. : {ip} 
PORT : {port}
Peer added to list!
```
Congratulations now you have successfully joined the network and now you can issue tx's and participate in the network.
## Usage
To issue a tx:
```bash
Node >> tx
```
To set coinbase:
```bash
Node >> coinbase
```
To mine an empty block:
```bash
Node >> mine empty
```
To check balance:
```bash
Node >> balance
```
To get node's address:
```bash
Node >> address
```
To manually sync (this will make you sync with your first connected peer/node again):
```bash
Node >> sync
```
To connect to a default peer:
```bash
Node >> default peer
```
To see other accounts balances:
```bash
Node >> see balance
```
To disable or enable incoming messages:
```bash
Node >> verbose
```
To disable or enable error tracebacking (disabled by default):
```bash
Node >> sys verbose
```
To disable or enable sending messages:
```bash
Node >> messaging
```
To check hashrate:
```bash
Node >> hashrate
```
To save settings:
```bash
Node >> save settings
```
To see building block:
```bash
Node >> top block
```
To preview longest chain:
```bash
Node >> longest branch
```
Typing anything else except these commands will send it as a message to all nodes if messaging is enabled(default).
# Others
Keypairs are stored in the same directory as the node.pyc file as "den.alukeys".
### To change the keys.
1. Replace the keypair file with a different keypair in the correct format.\
OR
2. Delete the keypair file. When the node is started next time a new keypair will be generated.
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.