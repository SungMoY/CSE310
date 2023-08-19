Screenshot descriptions:
pg1: HelloWorld.html file distributed from webserver.py (ip address)
pg2: HelloWorld.html file distributed from webserver.py (localhost)
pg3: webserver.py responding with 404 for a file that does not exist (ip address)
pg4: webserver.py responding with 404 for a file that does not exist (localhost)
pg5: chrome view of webserver.py responding with 404 for a file that does not exist (ip address)
pg6: HTTP-wireshark-file2.html sent through proxyserver.py
pg7: HTTP-wireshark-file3.html sent through proxyserver.py
pg8: HTTP-wireshark-file4.html sent through proxyserver.py
pg9: HTTP-wireshark-file4.html sent through proxyserver.py after a refresh

For pg9, only the image of the Pearson logo is cached. This is because a request for the second image
response with a 301 redirect. It was stated in this piazza post that this behavior is fine.
https://piazza.com/class/l72xfn146r2yt/post/65