/*
 * file   : libprun.c
 * author : ning
 * date   : 2013-03-13 00:14:27
 */

#include "libprun.h"

#define BUFF_SIZE 1024
connect_fun orig_connect = NULL;

void init(){
    if (orig_connect) //todo: threading
        return;

    void *funcptr = dlsym(RTLD_NEXT, "connect");
    orig_connect = funcptr;
}

/*char proxy_host[] = "127.0.0.1";*/
/*unsigned short proxy_port = 8888;*/

int connect_proxy(int sockfd, struct sockaddr_in *addr, socklen_t addrlen) {

    char * proxy_host = getenv ("PRUN_PROXY");
    char * pos = strchr(proxy_host, ':');
    int proxy_port = atol(pos+1);
    *pos = '\0';


    char *ip = inet_ntoa(addr->sin_addr);
    int port = addr->sin_port;
    unsigned char buf[BUFF_SIZE];
    int used = 0;
    int len = 0;
    

    struct sockaddr_in proxy_sa;
    memset(&proxy_sa, 0, sizeof(struct sockaddr_in));
    proxy_sa.sin_family = AF_INET;
    proxy_sa.sin_addr.s_addr = inet_addr(proxy_host);
    proxy_sa.sin_port = htons(proxy_port);

    int ret = orig_connect(sockfd, (struct sockaddr *)&proxy_sa, addrlen);
    PDEBUG("connect ret=%d\n", ret);

    char * s = getenv("PRUN_PROXY_PREFIX"); // like "CONNECT ", "GET /q?q="
    if(NULL == s){
        s = "CONNECT ";
    }

    len = snprintf((char *) buf, sizeof(buf), "%s%s:%d HTTP/1.0\r\n\r\n", s, ip, ntohs(port));

    PDEBUG("write len = %d\n", len);
    if(len != (size_t) send(sockfd, buf, len, 0)){
        PDEBUG("error on send len = %d\n", len);
        return ERROR;
    }
    used = 0;
    while(len = read(sockfd, buf+used, BUFF_SIZE - used)){
        used += len;
        if (buf[used-4] == '\r' && buf[used-3] == '\n' && buf[used-2] == '\r' && buf[used-1] == '\n' )
            break;
    }
    //HTTP/1.1 200 OK
    if (buf[9] == '2' && buf[9] == '0' && buf[9] == '0'){
        return SUCCESS;    
    }
    return ERROR;
}

int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen) {
    init();
    int sock_type=0;
    socklen_t optlen=0;
    int ret = 0;

    optlen = sizeof(sock_type);
    getsockopt(sockfd, SOL_SOCKET, SO_TYPE, &sock_type, &optlen);
    if(!(SOCKFAMILY(*addr) == AF_INET && sock_type == SOCK_STREAM)) //not tcp socket
        return orig_connect(sockfd, addr, addrlen);

    int flags = 0; // backup flags
    flags = fcntl(sockfd, F_GETFL, 0);
    if(flags & O_NONBLOCK) //we do our work on NON block mode
        fcntl(sockfd, F_SETFL, !O_NONBLOCK);

    ret = connect_proxy(sockfd, (struct sockaddr_in * )addr, addrlen);

    fcntl(sockfd, F_SETFL, flags);
    if(ret != SUCCESS)
        errno = ECONNREFUSED;
    return ret;
}

