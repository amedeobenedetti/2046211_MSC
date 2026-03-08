import { getState, getActuators, setActuator } from "./api.js"

async function loadSensors() {

    try {

        const data = await getState()

        const grid = document.getElementById("sensorGrid")
        grid.innerHTML = ""

        Object.values(data).forEach(sensor => {

            sensor.measurements.forEach(measure => {

                const card = document.createElement("div")
                card.className = "sensor-card"

                const statusClass =
                    sensor.status === "ok"
                        ? "status-ok"
                        : "status-warning"

                card.innerHTML = `
                    <div class="sensor-title">
                        ${sensor.source_name}
                    </div>

                    <div class="sensor-value">
                        ${measure.value} ${measure.unit}
                    </div>

                    <div class="sensor-unit">
                        ${measure.metric} (${measure.unit})
                    </div>

                    <div class="${statusClass}">
                        status: ${sensor.status}
                    </div>

                    <div class="sensor-timestamp">
                        ${new Intl.DateTimeFormat(
                            'en-US',
                            {
                                dateStyle: 'short',
                                timeStyle: 'short',
                                timeZone: 'Europe/Rome'
                            }
                        ).format(new Date(sensor.timestamp))}
                    </div>
                `

                grid.appendChild(card)

            })

        })

    } catch (err) {

        console.error("Error loading sensors:", err)

    }

}

async function loadActuators() {

    const actuators = await getActuators()

    const grid = document.getElementById("actuatorGrid")
    grid.innerHTML = ""

    actuators.forEach(act => {

        const card = document.createElement("div")
        card.className = "actuator-card"

        const button = document.createElement("button")
        button.textContent = act.state

        button.onclick = async () => {

            const newState = act.state === "ON" ? "OFF" : "ON"

            await setActuator(act.name, newState)

            loadActuators()
        }

        card.innerHTML = `<div>${act.name}</div>`
        card.appendChild(button)

        grid.appendChild(card)

    })

}

async function init() {

    await loadSensors()
    await loadActuators()

}

init()

setInterval(loadSensors, 5000)
setInterval(loadActuators, 5000)