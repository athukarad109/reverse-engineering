#include <stdio.h>
#include <stdlib.h>
#include <unistd.h> // Required for gethostname()

int main(void) {
    char hostname[1024]; // Declare a buffer to store the hostname
    // Call gethostname to retrieve the hostname and store it in the buffer
    // The second argument is the maximum size of the buffer
    if (gethostname(hostname, sizeof(hostname)) == 0) {
        printf("Hostname: %s\n", hostname); // Print the retrieved hostname
    } else {
        perror("gethostname"); // Print an error message if gethostname fails
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
