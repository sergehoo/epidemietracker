var simplemaps_countrymap_mapdata={
  main_settings: {
    //General settings
		width: "responsive", //or 'responsive'
    background_color: "#FFFFFF",
    background_transparent: "yes",
    border_color: "#ffffff",
    pop_ups: "detect",
    
		//State defaults
		state_description: "State description",
    state_color: "#88A4BC",
    state_hover_color: "#3B729F",
    state_url: "",
    border_size: 1.5,
    all_states_inactive: "no",
    all_states_zoomable: "yes",
    
		//Location defaults
		location_description: "Location description",
    location_url: "",
    location_color: "#FF0067",
    location_opacity: 0.8,
    location_hover_opacity: 1,
    location_size: 25,
    location_type: "square",
    location_image_source: "frog.png",
    location_border_color: "#FFFFFF",
    location_border: 2,
    location_hover_border: 2.5,
    all_locations_inactive: "no",
    all_locations_hidden: "no",
    
		//Label defaults
		label_color: "#ffffff",
    label_hover_color: "#ffffff",
    label_size: 16,
    label_font: "Arial",
    label_display: "auto",
    label_scale: "yes",
    hide_labels: "no",
    hide_eastern_labels: "no",
   
		//Zoom settings
		zoom: "yes",
    manual_zoom: "yes",
    back_image: "no",
    initial_back: "no",
    initial_zoom: "-1",
    initial_zoom_solo: "no",
    region_opacity: 1,
    region_hover_opacity: 0.6,
    zoom_out_incrementally: "yes",
    zoom_percentage: 0.99,
    zoom_time: 0.5,
    
		//Popup settings
		popup_color: "white",
    popup_opacity: 0.9,
    popup_shadow: 1,
    popup_corners: 5,
    popup_font: "12px/1.5 Verdana, Arial, Helvetica, sans-serif",
    popup_nocss: "no",
    
		//Advanced settings
		div: "map",
    auto_load: "yes",
    url_new_tab: "no",
    images_directory: "default",
    fade_time: 0.1,
    link_text: "View Website"
  },
  state_specific: {
    CIAB: {
      name: "Abidjan",
      description: "default",
      color: "default",
      hover_color: "default",
      url: "default"
    },
    CIBS: {
      name: "Bas-Sassandra",
      description: "default",
      color: "default",
      hover_color: "default",
      url: "default"
    },
    CICM: {
      name: "Comoé",
      description: "default",
      color: "default",
      hover_color: "default",
      url: "default"
    },
    CIDN: {
      name: "Denguélé",
      description: "default",
      color: "default",
      hover_color: "default",
      url: "default"
    },
    CIGD: {
      name: "Gôh-Djiboua",
      description: "default",
      color: "default",
      hover_color: "default",
      url: "default"
    },
    CILC: {
      name: "Lacs",
      description: "default",
      color: "default",
      hover_color: "default",
      url: "default"
    },
    CILG: {
      name: "Lagunes",
      description: "default",
      color: "default",
      hover_color: "default",
      url: "default"
    },
    CIMG: {
      name: "Montagnes",
      description: "default",
      color: "default",
      hover_color: "default",
      url: "default"
    },
    CISM: {
      name: "Sassandra-Marahoué",
      description: "default",
      color: "default",
      hover_color: "default",
      url: "default"
    },
    CISV: {
      name: "Savanes",
      description: "default",
      color: "default",
      hover_color: "default",
      url: "default"
    },
    CIVB: {
      name: "Vallée du Bandama",
      description: "default",
      color: "default",
      hover_color: "default",
      url: "default"
    },
    CIWR: {
      name: "Woroba",
      description: "default",
      color: "default",
      hover_color: "default",
      url: "default"
    },
    CIYM: {
      name: "Yamoussoukro",
      description: "default",
      color: "default",
      hover_color: "default",
      url: "default"
    },
    CIZZ: {
      name: "Zanzan",
      description: "default",
      color: "default",
      hover_color: "default",
      url: "default"
    }
  },
  locations: {
    "0": {
      name: "Yamoussoukro",
      lat: "6.820548",
      lng: "-5.276741"
    }
  },
  labels: {
    CIAB: {
      name: "Abidjan",
      parent_id: "CIAB"
    },
    CIBS: {
      name: "Bas-Sassandra",
      parent_id: "CIBS"
    },
    CICM: {
      name: "Comoé",
      parent_id: "CICM"
    },
    CIDN: {
      name: "Denguélé",
      parent_id: "CIDN"
    },
    CIGD: {
      name: "Gôh-Djiboua",
      parent_id: "CIGD"
    },
    CILC: {
      name: "Lacs",
      parent_id: "CILC"
    },
    CILG: {
      name: "Lagunes",
      parent_id: "CILG"
    },
    CIMG: {
      name: "Montagnes",
      parent_id: "CIMG"
    },
    CISM: {
      name: "Sassandra-Marahoué",
      parent_id: "CISM"
    },
    CISV: {
      name: "Savanes",
      parent_id: "CISV"
    },
    CIVB: {
      name: "Vallée du Bandama",
      parent_id: "CIVB"
    },
    CIWR: {
      name: "Woroba",
      parent_id: "CIWR"
    },
    CIYM: {
      name: "Yamoussoukro",
      parent_id: "CIYM"
    },
    CIZZ: {
      name: "Zanzan",
      parent_id: "CIZZ"
    }
  }
};