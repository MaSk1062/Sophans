const tooltipTriggerList = document.querySelectorAll('.tenant-doc-tt')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))