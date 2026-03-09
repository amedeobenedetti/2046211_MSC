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

    const response = await getActuators()
    const actuators = response.actuators

    const grid = document.getElementById("actuatorGrid")
    grid.innerHTML = ""
    
    Object.entries(actuators).forEach(([name, state]) => {

        const card = document.createElement("div")
        card.className = "actuator-card"

        const label = document.createElement("label")
        label.className = "switch"

        const input = document.createElement("input")
        input.type = "checkbox"
        input.checked = state === "ON"

        input.onchange = async () => {
            const newState = input.checked ? "ON" : "OFF"
            await setActuator(name, newState)
            
            setTimeout(await loadActuators(), 5000)
        }

        const slider = document.createElement("span")
        slider.className = "slider"

        label.appendChild(input)
        label.appendChild(slider)

        card.innerHTML = `<div>${name}</div>`
        card.appendChild(label)

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