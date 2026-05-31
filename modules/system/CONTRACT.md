# System Module Contract

This module answers:

```text
What machine is George running on?
```

## Allowed in v1

- read configured node name, role, environment, and log level
- read hostname
- read operating system and version
- read machine architecture
- read Python version
- read current working directory
- read project root
- read CPU count
- read memory total when practical
- read disk total/free for the project filesystem when practical
- read current timestamp

## Not Allowed in v1

- remote control
- process management
- service restart
- file editing
- shell command execution beyond safe read-only system info
- dashboard UI
- API routing

This module reports system state. It does not change system state.
