import { ctfConfig, type CtfConfig } from "$lib/schema";
import fs from "node:fs";


/**
 * Load services configuration from JSON file.
 * @param path Path of the file containing services config.
 * @returns CtfConfig
 */
export function loadConfig(path = "./ctf_config.json") {
    if (!fs.existsSync(path)) {
        let end_date = new Date();
        end_date.setTime(end_date.getTime() + 8 * 60 * 60 * 1000)
        return {
            start_date: new Date().toISOString().slice(0, -8),
            end_date: end_date.toISOString().slice(0, -8),
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
        let end_date = new Date();
        end_date.setTime(end_date.getTime() + 8 * 60 * 60 * 1000)
        return {
            start_date: new Date().toISOString().slice(0, -8),
            end_date: end_date.toISOString().slice(0, -8),
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
export function saveConfig(data: CtfConfig, path = "./ctf_config.json") {
    try {
        fs.writeFileSync(path, JSON.stringify(data));
    }
    catch (e) {
        console.error("Error writing to services config file.", e);
    }
}


export let CTF_CONFIG: CtfConfig = loadConfig();