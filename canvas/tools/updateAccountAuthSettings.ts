
import { tool } from "ai";
import { updateAccountAuthSettingsDataSchema } from "./aitm.schema.ts";
import { updateAccountAuthSettings, UpdateAccountAuthSettingsData } from "..";

export default tool({
  description: `
  update account auth settings
For various cases of mixed SSO configurations, you may need to set
some
configuration at the account level to handle the particulars of your
setup.

This endpoint
accepts a PUT request to set several possible account
settings. All setting are optional on each
request, any that are not
provided at all are simply retained as is.  Any that provide the key but
a
null-ish value (blank string, null, undefined) will be UN-set.

You can list the current state of
each setting with "show_sso_settings"
    `,
  parameters: updateAccountAuthSettingsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateAccountAuthSettingsData, "url"> ) => {
    try {
      const { data } = await updateAccountAuthSettings(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    