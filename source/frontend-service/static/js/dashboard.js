import { getState, getActuators, setActuator } from "./api.js"

const shownWarnings = new Set()
const telemetryCharts = {}
const telemetryData = {}

function createTelemetryChart(name, metric) {

    const grid = document.getElementById("telemetryGrid")

    const container = document.createElement("div")
    container.className = "telemetry-card"

    const canvas = document.createElement("canvas")

    container.innerHTML = `<h3>${name}</h3>`
    container.appendChild(canvas)

    grid.appendChild(container)

    const chart = new Chart(canvas, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: metric,
                data: []
            }]
        },
        options: {
            responsive: true,
            animation: false
        }
    })

    telemetryCharts[name] = chart
    telemetryData[name] = []

}

function updateTelemetry(sensor) {

    const name = sensor.source_name

    const measure = sensor.measurements[0]

    if (!telemetryCharts[name]) {

        createTelemetryChart(name, measure.metric)

    }

    const chart = telemetryCharts[name]

    chart.data.labels.push(
        new Date(sensor.timestamp).toLocaleTimeString()
    )

    chart.data.datasets[0].data.push(measure.value)

    if (chart.data.labels.length > 20) {

        chart.data.labels.shift()
        chart.data.datasets[0].data.shift()

    }

    chart.update()

}

function showNotification(message) {

    const container = document.getElementById("notificationContainer")

    const notif = document.createElement("div")
    notif.className = "notification"
    notif.textContent = message

    container.appendChild(notif)

    setTimeout(() => {
        notif.remove()
    }, 5000)

}

async function loadSensors() {

    try {
        const data = await getState()
        const grid = document.getElementById("sensorGrid")
        grid.innerHTML = ""

        Object.values(data).forEach(sensor => {
            if (sensor.source_kind === "telemetry_topic") {
                updateTelemetry(sensor)
            }
            if (sensor.status === "warning") {
                const key = sensor.source_name + sensor.timestamp
                if (!shownWarnings.has(key)) {
                    showNotification(`Warning from ${sensor.source_name}`)
                    shownWarnings.add(key)
                }
            }
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
            
            setTimeout(loadActuators, 5000)
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