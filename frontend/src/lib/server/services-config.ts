import { servicesConfig, type ServicesConfig } from "$lib/schema";
import fs from "node:fs";
import path from "node:path";


/**
 * Load services configuration from JSON file.
 * @param path Path of the file containing services config.
 * @returns ServicesConfig
 */
export function loadServicesConfig(path = "./services_config.json") {
    if (!fs.existsSync(path)) {
        return {};
    }

    try {
        let data = servicesConfig.parse(JSON.parse(fs.readFileSync(path, "utf-8")));

        return data;
    }
    catch (e) {
        console.error("Error parsing services config, returning empty object.");
        return {};
    }
}

/**
 * Save services configuration to JSON file with file locking.
 * @param data Services config to save in the file.
 * @param path Path where to save the file.
 */
export function saveServicesConfig(data: ServicesConfig, path = "./services_config.json") {
    try {
        fs.writeFileSync(path, JSON.stringify(data));
    }
    catch (e) {
        console.error("Error writing to services config file.", e);
    }
}