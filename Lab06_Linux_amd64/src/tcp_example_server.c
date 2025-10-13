#include <stdio.h>
#include <string.h>
#include <sys/types.h>

#ifdef _WIN32
#include <WinSock2.h>
#include <WS2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")
#else
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

int main() {
	int s = socket(AF_INET, SOCK_STREAM, 0);
	struct sockaddr_in sa;

	// Bind to 0.0.0.0:12345 (all interfaces, port 12345)
	sa.sin_family = AF_INET;
	sa.sin_addr.s_addr = htonl(INADDR_ANY); // all interfaces
	sa.sin_port = htons(12345);
	bind(s, (struct sockaddr*) &sa, sizeof(sa));
	// Now, open the port
	listen(s, 1);

	// Accept connection indefinitely, but just one at a time
	while (1) {
		int c = accept(s, 0, 0);
		fprintf(stderr, "New connection\n");
		char buf[1024];
		// Echo the received data until the client closes the connection
		while (1) {
			int len = recv(c, buf, sizeof(buf), 0);
			if (len == 0) {
				fprintf(stderr, "Connection closed\n");
				break;
			}
			fwrite(buf, 1, len, stdout);
		}
	}
	// I should never get here, but for form's sake, close the server socket`
	close(s);
	return 0;
}
