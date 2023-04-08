function removeTrack(pressedRow) {
    /* This method will delete a row */
    pressedRow.parentNode.parentNode.remove();
    }

function transferTrack(pressedRow) {
      // Get the clicked row and its first data cell
      const clickedRow = pressedRow.parentNode.parentNode;
      const clickedCell = clickedRow.querySelector('td:first-child');

      // New row with a copy of the first cell of the clicked row
      const playlistTable = document.getElementById('playListTable');
      const playlistTBody = playlistTable.tBodies[0];
      const newRow = playlistTBody.insertRow(1);
      const newCell = newRow.insertCell(0);
      newCell.className = clickedCell.className;
      newCell.setAttribute('data-song-id', clickedCell.getAttribute('data-song-id'));
      newCell.textContent = clickedCell.textContent;

      // new row add a remove button
      const removeButton = document.createElement('button');
      removeButton.type = 'button';
      removeButton.className = 'btn btn-danger';
      removeButton.textContent = 'Remove';
      removeButton.addEventListener('click', function() {
        removeTrack(this);
      });

      const removeCell = newRow.insertCell(1);
      removeCell.classList.add('move-cell');
      removeCell.appendChild(removeButton);
      pressedRow.parentNode.parentNode.remove();
}

// loading picked tracks into list - they may or may not be saved
function get_playlist_ids()
{
    var tableData=[];
    var table = document.querySelector('#playListTable');
    var rows = table.querySelectorAll('tr');

    for (var i = 0; i < rows.length; i++) {
        var tdElements = rows[i].querySelectorAll('td');
        for (var j = 0; j < tdElements.length; j++) {
            var idValue = tdElements[j].getAttribute('data-song-id');
            if (idValue) {
                tableData.push(idValue);
            }
        }
    }
    return tableData;
}

//Get Official Playlist get_official_album
function officialSoundtrack() {
  // Get the ids from the picked playlist so there is no repeat
  const tableData = get_playlist_ids();
  fetchAndHandleResponse('/getSongData', {table_data: tableData }, "Pick From Official PlayTrack...");

}
//Get recommended tracks from spotify based on official playlist
function getRecommendedracks() {
  // Get the ids from the picked playlist so there is no repeat
  const tableData = get_playlist_ids();
  fetchAndHandleResponse('/getRecommendedTracks', {table_data: tableData }, "Pick From Recommended Tracks...");

}

function searchTracks() {
  const tableData = get_playlist_ids();
  const songName = document.getElementById("song-name").value;
  fetchAndHandleResponse('/searchForMatchingTracks', { song_name: songName, table_data: tableData }, "Pick from Searched Tracks...");
}

function fetchAndHandleResponse(url, data, title) {
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    const tbody = document.getElementById("tbodyrec");
    tbody.innerHTML = '<tr><th class="table-border-none">'+title+'</th></tr>';
    for (var i = 0; i < data.length; i++) {
      var row = tbody.insertRow();
      var cell1 = row.insertCell(0);
      var cell2 = row.insertCell(1);
      cell1.innerHTML = data[i][0];

      cell2.innerHTML = '<button type="button" class="btn btn-danger" onclick="transferTrack(this)">Add</button>';
      cell1.setAttribute("class", "btn rec-table-button");
      cell1.setAttribute("data-song-id", data[i][1]);
    }
  })
  .catch(error => {
    window.location.href = "{{ url_for('dashboard') }}";

  });
}

async function saveTracks() {
  const tableData = get_playlist_ids();

  const response = await fetch('/updateTracks', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({table_data: tableData})
  });

  if (response.ok) {
    console.log('Table data was successfully sent to the server');
  } else {
    console.error('Network response was not ok');
    window.location.href = "{{ url_for('dashboard') }}";

  }
}

