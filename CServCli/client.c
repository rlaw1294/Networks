#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <arpa/inet.h>


int main( int argc, char *argv[] )
{
  int sockfd = 0,n = 0;
  char recvBuff[1024];
  struct sockaddr_in serv_addr;

  //socket()
  memset(recvBuff, '0' ,sizeof(recvBuff));
  if((sockfd = socket(AF_INET, SOCK_STREAM, 0))< 0)
    {
      printf("\n Error : Could not create socket \n");
      return 1;
    }

  serv_addr.sin_family = AF_INET;
  serv_addr.sin_port = htons(5000);
  //  serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");                                                                                  
  serv_addr.sin_addr.s_addr;

  struct hostent *hen;
  hen = gethostbyname("rachel.cs164");

  if (hen==NULL) {
    fprintf(stdout, "HOST NOT FOUND");
    exit(1);
  }

  bcopy((char *)hen->h_addr,(char *)&serv_addr.sin_addr.s_addr,hen->h_length);

  
  //connect()
  if(connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr))<0)
    {
      printf("\n Error : Connect Failed \n");
      return 1;
    }

  //write()
  write(sockfd, argv[1], strlen(argv[1])+1);

  //read()
  while((n = read(sockfd, recvBuff, sizeof(recvBuff)-1)) > 0)
    {
      recvBuff[n] = 0;
      if(fputs(recvBuff, stdout) == EOF)
        {
          printf("\n Error : Fputs error");
        }
      printf("\n");
    }
  if( n < 0)
    {
      printf("\n Read Error \n");
    }
  write(sockfd, argv[1], strlen(argv[1])+1);

  while((n = read(sockfd, recvBuff, sizeof(recvBuff)-1)) > 0)
    {
      recvBuff[n] = 0;
      if(fputs(recvBuff, stdout) == EOF)
        {
          printf("\n Error : Fputs error");
        }
      printf("\n");
    }

  if( n < 0)
    {
      printf("\n Read Error \n");
    }


  return 0;
}





