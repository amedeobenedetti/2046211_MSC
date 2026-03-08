const API_BASE = "http://localhost:8004"

async function getSensors() {
    const res = await fetch(API_BASE + "/sensors")
    return await res.json()
}

async function getActuators() {
    const res = await fetch(API_BASE + "/actuators")
    return await res.json()
}

async function setActuator(name, state) {

    await fetch(API_BASE + "/actuators/" + name, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            state: state
        })
    })
}

async function getRules() {
    const res = await fetch(API_BASE + "/rules")
    return await res.json()
}

async function createRule(rule) {

    await fetch(API_BASE + "/rules", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(rule)
    })
}