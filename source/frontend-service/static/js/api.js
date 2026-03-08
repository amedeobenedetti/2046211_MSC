const DASHBOARD_API = "http://localhost:8003"
const ACTUATOR_API = "http://localhost:8004"
const RULE_API = "http://localhost:8001"


export async function getState() {
    const res = await fetch(DASHBOARD_API + "/state")
    return await res.json()
}

export async function getActuators() {
    const res = await fetch(ACTUATOR_API + "/actuators")
    return await res.json()
}

export async function setActuator(name, command) {

    await fetch(ACTUATOR_API + "/actuators/" + name, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            command: command
        })
    })
}

export async function getRules() {
    const res = await fetch(RULE_API + "/rules")
    return await res.json()
}