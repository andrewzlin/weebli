document.addEventListener('DOMContentLoaded', () => {
  getRecommendations();
});

function getRecommendations() {
  const animeSelect = document.getElementById('animeSelect');
  const anime_mal_Id = animeSelect.value;

  if (!anime_mal_Id) {
    print('Please select an anime');
    return;
  }

  const formData = new FormData()
  formData.append('anime_mal_Id', anime_mal_Id)
  

  fetch('/get-recommendations', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
            alert(data.error);
            return;
        }

    const listDiv = document.getElementById('recommendationsList')
    listDiv.innerHTML = '<br></br>';
    
    data.recommendations.forEach(anime =>{
      const animeElement = `
              <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <img src="${anime.main_picture}" alt="${anime.title}" style="width: 100px; margin-right: 10px;">
                <p style="margin-right: 20px; flex-grow: 1;">${anime.title}</p>
                <form class="add-form" data-anime-mal-id="${anime.id}">
                  <button type="submit" class="add-button" style="margin-left: auto;">Add To Plan To Watch</button>
                </form>
              </div>
            `;
      listDiv.innerHTML += animeElement;
    });

    if (data.recommendations.length === 0) {
    listDiv.innerHTML = '<p>No recommendations found for this anime.</p>';
    }

    document.getElementById('recommendationsResult').style.display = 'block';
  })
}