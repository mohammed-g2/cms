(function (moment) {
    let timeFields = document.getElementsByClassName('time');
    for (let i = 0; i < timeFields.length; i++) {
        let utc = moment.utc(timeFields[i].textContent).toDate();
        let local = moment(utc).local().fromNow();
        timeFields[i].innerHTML = local;
    }
})(moment);