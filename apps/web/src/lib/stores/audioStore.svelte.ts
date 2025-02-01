interface Track {
  id: string;
  title: string;
  artist: string;
  coverArt: string;
  audioUrl: string;
}

class AudioStore {
  currentTrack = $state<Track | null>(null);

  playTrack(track: Track) {
    this.currentTrack = track;
  }

  clearTrack() {
    this.currentTrack = null;
  }
}

// Create and export a singleton instance
export const audioStore = new AudioStore();
