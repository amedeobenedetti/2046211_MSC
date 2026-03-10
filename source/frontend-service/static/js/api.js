const DASHBOARD_API = "http://localhost:8003"


export async function getState() {
    const res = await fetch(DASHBOARD_API + "/state")
    return await res.json()
}

export async function getActuators() {
    const res = await fetch(DASHBOARD_API + "/actuators")
    return await res.json()
}

export async function setActuator(name, command) {

    await fetch(DASHBOARD_API + "/actuators/" + name, {
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
    const res = await fetch(DASHBOARD_API + "/rules")
    return await res.json()
}

export async function createRule(rule) {
    await fetch(DASHBOARD_API + "/rule", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            rule: rule
        })
    })
}

export async function updateRule(rule) {
    await fetch(DASHBOARD_API + "/rules/" + rule.id, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            rule: rule
        })
    })
}

export async function setRuleState(ruleId, state) {
    await fetch(DASHBOARD_API + "/rules/" + ruleId, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            state: state
        })
    })
}

export async function deleteRule(ruleId) {
    await fetch(DASHBOARD_API + "/rules/" + ruleId, {
        method: "DELETE"
    })
}
