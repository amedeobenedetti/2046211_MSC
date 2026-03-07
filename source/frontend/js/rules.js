async function loadRules() {

    const rules = await getRules()

    const container = document.getElementById("rules")
    container.innerHTML = ""

    rules.forEach(r => {

        const div = document.createElement("div")

        div.innerText =
            "IF "
            + r.sensor_name
            + " "
            + r.operator
            + " "
            + r.threshold
            + " THEN "
            + r.actuator_name
            + " "
            + r.target_state

        container.appendChild(div)
    })
}

document.getElementById("ruleForm").onsubmit = async (e) => {

    e.preventDefault()

    const rule = {
        sensor_name: document.getElementById("sensor").value,
        metric_name: document.getElementById("metric").value,
        operator: document.getElementById("operator").value,
        threshold: parseFloat(document.getElementById("threshold").value),
        actuator_name: document.getElementById("actuator").value,
        target_state: document.getElementById("state").value
    }

    await createRule(rule)

    loadRules()
}

loadRules()