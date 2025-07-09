
import { tool } from "ai";
import { showAccountAuthSettingsDataSchema } from "./aitm.schema.ts";
import { showAccountAuthSettings, ShowAccountAuthSettingsData } from "..";

export default tool({
  description: `
  show account auth settings
The way to get the current state of each account level setting
that's
relevant to Single Sign On configuration

You can list the current state of each setting with
"update_sso_settings"
    `,
  parameters: showAccountAuthSettingsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowAccountAuthSettingsData, "url"> ) => {
    try {
      const { data } = await showAccountAuthSettings(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    