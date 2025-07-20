import { addService, deleteService, editRefreshRate } from "$lib/schema";
import { CTF_CONFIG, saveConfig } from "$lib/server/config";
import type { Actions, PageServerLoad } from "./$types";
import { fail, superValidate, message } from "sveltekit-superforms";
import { zod4 } from "sveltekit-superforms/adapters";


export const load: PageServerLoad = async ({}) => {
    return {
        ctfConfig: CTF_CONFIG,
        addServiceForm: await superValidate(zod4(addService)),
        deleteServiceForm: await superValidate(zod4(deleteService)),
        editRefreshRateForm: await superValidate(zod4(editRefreshRate))
    };
};

export const actions = {
    addService: async ({ request }) => {
        const form = await superValidate(request, zod4(addService));
        
        if (!form.valid) {
            return fail(400, { form });
        }

        if (CTF_CONFIG.services[form.data.name]) {
            delete CTF_CONFIG.services[form.data.name];
        }

        CTF_CONFIG.services[form.data.name] = {
            color: form.data.color,
            ipports: form.data.ports.split(",").map((v) => `${form.data.serviceIP}:${v}`)
        }

        saveConfig(CTF_CONFIG);

        return message(form, `Service ${form.data.name} created.`);
    },
    deleteService: async ({ request }) => {
        const form = await superValidate(request, zod4(deleteService));

        if (!form.valid) {
            return fail(400, { form });
        }

        if (CTF_CONFIG.services[form.data.name]) {
            delete CTF_CONFIG.services[form.data.name];
            saveConfig(CTF_CONFIG);
            return message(form, `Service ${form.data.name} deleted.`);
        }

        return fail(400, { form });
    },
    editRefreshRate: async ({ request }) => {
        const form = await superValidate(request, zod4(editRefreshRate));

        if (!form.valid) {
            return fail(400, { form });
        }

        CTF_CONFIG.refresh_rate = form.data.refreshRate;

        saveConfig(CTF_CONFIG);

        return message(form, "Refresh rate updated.");
    }
} satisfies Actions;