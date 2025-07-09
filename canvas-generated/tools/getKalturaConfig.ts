
import { tool } from "ai";
import { getKalturaConfigDataSchema } from "./aitm.schema.ts";
import { getKalturaConfig, GetKalturaConfigData } from "..";

export default tool({
  description: `
  Get Kaltura config
Return the config information for the Kaltura plugin in json format.
    `,
  parameters: getKalturaConfigDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetKalturaConfigData, "url"> ) => {
    try {
      const { data } = await getKalturaConfig(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    