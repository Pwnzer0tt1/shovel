import { ctfConfig, type CtfConfig } from "$lib/schema";
import fs from "node:fs";


/**
 * Load services configuration from JSON file.
 * @param path Path of the file containing services config.
 * @returns CtfConfig
 */
export function loadConfig(path = "./services_config.json") {
    if (!fs.existsSync(path)) {
        return {
            start_date: "1970-01-01T00:00+00:00",
            tick_length: 120,
            refresh_rate: 120,
            services: {}
        };
    }

    try {
        let data = ctfConfig.parse(JSON.parse(fs.readFileSync(path, "utf-8")));
        return data;
    }
    catch (e) {
        console.error("Error parsing services config, returning default values.");
        return {
            start_date: "1970-01-01T00:00+00:00",
            tick_length: 120,
            refresh_rate: 120,
            services: {}
        };
    }
}

/**
 * Save services configuration to JSON file with file locking.
 * @param data Config to save in the file.
 * @param path Path where to save the file.
 */
export function saveConfig(data: CtfConfig, path = "./services_config.json") {
    try {
        fs.writeFileSync(path, JSON.stringify(data));
    }
    catch (e) {
        console.error("Error writing to services config file.", e);
    }
}


export let CTF_CONFIG: CtfConfig = loadConfig();