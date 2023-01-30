# deepstream app coordinator

NOTE: this page using `mermaid` to create graph, but `gitea` doesn't support it.
One could go to <mermaid.live> and paste the mermaid code to view diagrams.

## TODO

- [x] define config schema for deepstream-app
- [x] define topics schema
- [ ] develop agent using docker python api
- [ ] develop coordinator using what?
- [ ] how to handle deepstream-app updating?

## Design

```mermaid
graph TD
    A(frontend) ---|interact | B(Coordinator)
    B ---|kafka async| C[Agent 1]
    B ---id1[(sqlite)]
    B ---|kafka async| D[Agent 2]
    C -->|Docker API| E[Deepstream instance 1.1]
    C -->|Docker API| F[Deepstream instance 1.2]
    D -->|Docker API| G[Deepstream instance 2.1]
    D -->|Docker API| H[Deepstream instance 2.2]
```

- The `Deepstream instance` is a deepstream container, and we need to know it's configuration schema.
- `Agent`s use `python docker sdk` to manage all `Deepstream instance` instances. It can read, write instances' configuraion, up/down the containers, and monitor the containers' status.
- `Coordinator` is a fullstack app, which interact with `Agent` **asynchronously** using `kafka`

## Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant C as Coordinator
    participant A as Agent
    participant D as Deepstream-app
    Note over U,C: Typical backend-frontend interaction
    Note over C,A: Async through Kafka
    Note over A,D: Docker Python API

    rect rgb(100, 100, 100)
    activate C
    A-)C: Greating, I'm "agent_id", here's the info about me (topic 200)
    C->>C: Update vào database
    C--)A: You are allowed to enter our system (topic 201)
    deactivate C
    end

    rect rgb(200, 200, 200)
    U->>U: CRUD camera, chọn mode (debug or not)
    U->>C: Tạo update request
    activate C
    C->>C: Update vào database
    C-->>U: Hear you, will update soon
    C->>C: Generate new configuration
    C-)+A: new configuration (topic 210)
    deactivate C
    A->>A: Tự đối chiếu configuration
    A->>+D: Delete or Create container
    D-->>-A: Im up already
    A--)-C: done (topic 220)
    activate C
    C-->>U: update UI
    deactivate C
    end

    rect rgb(200, 200, 200)
    loop Every minute
    activate A
    A->>+D: All instance are OK?
    D-->>-A: Status of instances
    A-)C: I'm doing great, here's my status (topic 220)
    deactivate A
    end
    end
```