import { getRules, createRule, updateRule, deleteRule } from './api.js';


const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function loadRules() {

    const rules = await getRules()

    const container = document.getElementById("rules")
    container.innerHTML = ""

    rules.forEach(r => {

        const form = document.createElement("form")

        const id = "rule" + r.id

        form.innerHTML = `
            IF
            <input id="${id}sensor_name" value="${r.sensor_name}">
            <input id="${id}metric_name" value="${r.metric_name}">
            <select id="${id}operator">
                <option ${r.operator == ">" ? "selected" : ""}>></option>
                <option ${r.operator == "<" ? "selected" : ""}>&lt;</option>
                <option ${r.operator == ">=" ? "selected" : ""}>>=</option>
                <option ${r.operator == "<=" ? "selected" : ""}>&lt;=</option>
                <option ${r.operator == "=" ? "selected" : ""}>=</option>
            </select>
            <input id="${id}threshold_value" type="number" value="${r.threshold_value}">
            THEN
            <input id="${id}actuator_name" value="${r.actuator_name}">
            <select id="${id}target_state">
                <option ${r.target_state == "ON" ? "selected" : ""}>ON</option>
                <option ${r.target_state == "OFF" ? "selected" : ""}>OFF</option>
            </select>
            <button type="submit">Update</button>
            <button type="button" id="${id}delete">Delete</button>
        `

        form.onsubmit = async e => {
            e.preventDefault()

            const rule = {
                id: r.id,
                name: r.name,
                sensor_name: document.getElementById(id + "sensor_name").value,
                metric_name: document.getElementById(id + "metric_name").value,
                operator: document.getElementById(id + "operator").value,
                threshold_value: parseFloat(document.getElementById(id + "threshold_value").value),
                actuator_name: document.getElementById(id + "actuator_name").value,
                target_state: document.getElementById(id + "target_state").value
            }

            await updateRule(rule)
            sleep(3000).then(() => {
                loadRules()
            })
        }
        
        container.appendChild(form)
        
        document.getElementById(id + "delete").onclick = async () => {
            await deleteRule(r.id)
            sleep(3000).then(() => {
                loadRules()
            })
        }

    })
}

document.getElementById("ruleForm").onsubmit = async (e) => {

    e.preventDefault()

    const rule = {
        sensor_name: document.getElementById("sensor").value,
        metric_name: document.getElementById("metric").value,
        operator: document.getElementById("operator").value,
        threshold_value: parseFloat(document.getElementById("threshold").value),
        actuator_name: document.getElementById("actuator").value,
        target_state: document.getElementById("state").value
    }

    await createRule(rule)

    loadRules()
}

loadRules()