(function(){
  const owner = 'rulingAnts';
  const repo = 'SFM-Text-Splitter';
  const assetName = 'SFM Text Splitter.zip';

  const btn = document.getElementById('download-btn');
  const status = document.getElementById('download-status');

  async function loadLatest(){
    try {
      status.textContent = 'Fetching latest release...';
      const res = await fetch(`https://api.github.com/repos/${owner}/${repo}/releases/latest`, {
        headers: { 'Accept': 'application/vnd.github+json' }
      });
      if(!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if(!data.assets || !Array.isArray(data.assets)) throw new Error('No assets found');
      let asset = data.assets.find(a => a && a.name === assetName);
      if(!asset){
        // fallback: first .zip asset
        asset = data.assets.find(a => a && typeof a.name === 'string' && a.name.toLowerCase().endsWith('.zip'));
      }
      if(!asset) throw new Error('No zip asset found');
      btn.href = asset.browser_download_url;
      status.textContent = `Latest: ${data.tag_name}`;
    } catch(err){
      console.error(err);
      status.textContent = 'Unable to fetch release. Please check GitHub releases.';
      btn.classList.remove('btn-primary');
    }
  }

  if(btn && status){ loadLatest(); }
})();
