/*
 * file   : libprun.h
 * author : ning
 * date   : 2013-03-13 17:26:12
 */

#ifndef _LIBPRUN_H_
#define _LIBPRUN_H_


#include <sys/types.h>
#include <sys/param.h>

#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/socket.h>


#define     satosin(x)      ((struct sockaddr_in *) &(x))
#define     SOCKADDR(x)     (satosin(x)->sin_addr.s_addr)
#define     SOCKADDR_2(x)     (satosin(x)->sin_addr)
#define     SOCKPORT(x)     (satosin(x)->sin_port)
#define     SOCKFAMILY(x)     (satosin(x)->sin_family)


typedef int (*connect_fun)(int, const struct sockaddr *, socklen_t);

typedef enum {
    SUCCESS=0,
    ERROR =0,
} ERR_CODE;


#ifdef DEBUG
#define PDEBUG(fmt, args...) do { fprintf(stderr,"DEBUG:"fmt, ## args); fflush(stderr); } while(0)
#else
#define PDEBUG(fmt, args...) do {} while (0)
#endif

#endif
