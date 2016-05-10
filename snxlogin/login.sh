#!/usr/bin/expect -f

set user [lindex $argv 0]
set pass [lindex $argv 1]
set host [lindex $argv 2]

spawn snx -s $host -u $user

expect "Please enter your password:" {
    send "$pass\r\n"
}
expect {
    "SNX: Connection aborted" {
        send_user "Login Failed: $user:$pass\n"
    }
    send_user "Login Successful: $user:$pass\n"
}
