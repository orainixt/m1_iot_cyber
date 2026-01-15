#ifndef _LWIPOPTS_H
#define _LWIPOPTS_H

#define NO_SYS                      1 // 0 if RTOS 1 if bare metal  
#define LWIP_SOCKET                 0
#define LWIP_NETCONN                0 
#define SYS_LIGHTWEIGHT_PROT        1 

#define MEM_LIBC_MALLOC             0  
#define MEM_ALIGNMENT               4
#define MEM_SIZE                    4000
#define MEMP_NUM_TCP_SEG            32
#define PBUF_POOL_SIZE              24

#define LWIP_ARP                    1
#define LWIP_ETHERNET               1
#define LWIP_IPV4                   1
#define LWIP_ICMP                   1
#define LWIP_DHCP                   1
#define LWIP_DNS                    1

#define LWIP_SNTP                   1  
#define SNTP_SERVER_DNS             1  
#define SNTP_DEBUG                  LWIP_DBG_ON

#define TCPIP_THREAD_NAME           "TCP/IP"
#define TCPIP_THREAD_STACKSIZE      2048
#define TCPIP_THREAD_PRIO           3
#define TCPIP_MBOX_SIZE             6

#define CHECKSUM_GEN_IP             0
#define CHECKSUM_GEN_UDP            0
#define CHECKSUM_GEN_TCP            0
#define CHECKSUM_CHECK_IP           0
#define CHECKSUM_CHECK_UDP          0
#define CHECKSUM_CHECK_TCP          0

#define LWIP_DEBUG                  0 
#define SNTP_DEBUG                  LWIP_DBG_OFF

#endif
