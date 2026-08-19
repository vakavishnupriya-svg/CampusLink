/* Campus Event Pro - Full Interactive Calendar Engine */

let currentDate = new Date();
let currentView = 'month';
let calendarEvents = [];

document.addEventListener('DOMContentLoaded', () => {
  const calendarGrid = document.getElementById('calendar-grid');
  if (!calendarGrid) return;

  setupCalendarControls();
  fetchAndRenderCalendar();
});

function setupCalendarControls() {
  document.getElementById('prev-month-btn')?.addEventListener('click', () => {
    if (currentView === 'month') currentDate.setMonth(currentDate.getMonth() - 1);
    if (currentView === 'week') currentDate.setDate(currentDate.getDate() - 7);
    if (currentView === 'day') currentDate.setDate(currentDate.getDate() - 1);
    if (currentView === 'year') currentDate.setFullYear(currentDate.getFullYear() - 1);
    fetchAndRenderCalendar();
  });

  document.getElementById('next-month-btn')?.addEventListener('click', () => {
    if (currentView === 'month') currentDate.setMonth(currentDate.getMonth() + 1);
    if (currentView === 'week') currentDate.setDate(currentDate.getDate() + 7);
    if (currentView === 'day') currentDate.setDate(currentDate.getDate() + 1);
    if (currentView === 'year') currentDate.setFullYear(currentDate.getFullYear() + 1);
    fetchAndRenderCalendar();
  });

  document.getElementById('today-btn')?.addEventListener('click', () => {
    currentDate = new Date();
    fetchAndRenderCalendar();
  });

  const viewBtns = document.querySelectorAll('.view-btn');
  viewBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      viewBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentView = btn.dataset.view;
      renderCalendarView();
    });
  });

  const deptFilter = document.getElementById('calendar-dept-filter');
  const catFilter = document.getElementById('calendar-cat-filter');
  if (deptFilter) deptFilter.addEventListener('change', renderCalendarView);
  if (catFilter) catFilter.addEventListener('change', renderCalendarView);
}

async function fetchAndRenderCalendar() {
  try {
    calendarEvents = await APIClient.request('/api/calendar/events');
    renderCalendarView();
  } catch (err) {
    console.error('Failed to fetch calendar events', err);
  }
}

function renderCalendarView() {
  const titleDisplay = document.getElementById('calendar-month-year');
  const grid = document.getElementById('calendar-grid');

  const deptFilterVal = document.getElementById('calendar-dept-filter')?.value || 'All';
  const catFilterVal = document.getElementById('calendar-cat-filter')?.value || 'All';

  const filteredEvents = calendarEvents.filter(ev => {
    const matchDept = (deptFilterVal === 'All' || ev.department === deptFilterVal);
    const matchCat = (catFilterVal === 'All' || ev.category === catFilterVal);
    return matchDept && matchCat;
  });

  if (currentView === 'month') {
    renderMonthView(grid, titleDisplay, filteredEvents);
  } else if (currentView === 'week') {
    renderWeekView(grid, titleDisplay, filteredEvents);
  } else if (currentView === 'day') {
    renderDayView(grid, titleDisplay, filteredEvents);
  } else {
    renderYearView(grid, titleDisplay, filteredEvents);
  }
}

function renderMonthView(grid, titleDisplay, events) {
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  if (titleDisplay) titleDisplay.textContent = `${monthNames[month]} ${year}`;

  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  let html = `
    <div class="calendar-day-head">Sun</div>
    <div class="calendar-day-head">Mon</div>
    <div class="calendar-day-head">Tue</div>
    <div class="calendar-day-head">Wed</div>
    <div class="calendar-day-head">Thu</div>
    <div class="calendar-day-head">Fri</div>
    <div class="calendar-day-head">Sat</div>
  `;

  for (let i = 0; i < firstDay; i++) {
    html += `<div class="calendar-cell other-month"></div>`;
  }

  const today = new Date();

  for (let day = 1; day <= daysInMonth; day++) {
    const isToday = (today.getDate() === day && today.getMonth() === month && today.getFullYear() === year);
    const cellDateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

    const dayEvents = events.filter(ev => ev.start_time.startsWith(cellDateStr));

    html += `
      <div class="calendar-cell ${isToday ? 'today' : ''}">
        <span class="cell-date">${day}</span>
        ${dayEvents.map(ev => `
          <div class="calendar-event-pill event-cat-${ev.category}" onclick="openEventModal(${ev.id})">
            ${ev.title}
          </div>
        `).join('')}
      </div>
    `;
  }

  grid.style.gridTemplateColumns = 'repeat(7, 1fr)';
  grid.innerHTML = html;
}

function renderWeekView(grid, titleDisplay, events) {
  if (titleDisplay) titleDisplay.textContent = `Week View - ${currentDate.toLocaleDateString()}`;
  grid.style.gridTemplateColumns = 'repeat(7, 1fr)';
  grid.innerHTML = `<div style="grid-column: span 7; padding:2rem; text-align:center;">Showing upcoming schedule for current week.</div>`;
}

function renderDayView(grid, titleDisplay, events) {
  if (titleDisplay) titleDisplay.textContent = `Day View - ${currentDate.toLocaleDateString()}`;
  grid.style.gridTemplateColumns = '1fr';
  grid.innerHTML = `<div style="padding:2rem; text-align:center;">Full daily agenda view.</div>`;
}

function renderYearView(grid, titleDisplay, events) {
  if (titleDisplay) titleDisplay.textContent = `Year ${currentDate.getFullYear()}`;
  grid.style.gridTemplateColumns = 'repeat(4, 1fr)';
  grid.innerHTML = `<div style="grid-column: span 4; padding:2rem; text-align:center;">Annual Academic Calendar Overview.</div>`;
}

window.openEventModal = async function(eventId) {
  try {
    const ev = await APIClient.request(`/api/events/${eventId}`);
    const modalOverlay = document.getElementById('event-modal');
    if (!modalOverlay) return;

    document.getElementById('modal-event-title').textContent = ev.title;
    document.getElementById('modal-event-dept').textContent = `${ev.category} | ${ev.department}`;
    document.getElementById('modal-event-time').textContent = `📅 ${new Date(ev.start_time).toLocaleString()} to ${new Date(ev.end_time).toLocaleTimeString()}`;
    document.getElementById('modal-event-venue').textContent = `📍 ${ev.venue}`;
    document.getElementById('modal-event-desc').textContent = ev.description;
    document.getElementById('modal-event-seats').textContent = `${ev.seats_taken}/${ev.capacity} Seats Taken`;
    document.getElementById('modal-event-link').href = `event-details.html?id=${ev.id}`;

    modalOverlay.classList.add('active');
  } catch (err) {
    APIClient.showToast('Failed to load event details', 'error');
  }
};

window.closeEventModal = function() {
  document.getElementById('event-modal')?.classList.remove('active');
};
