
import { tool } from "ai";
import { startKalturaSessionDataSchema } from "./aitm.schema.ts";
import { startKalturaSession, StartKalturaSessionData } from "..";

export default tool({
  description: `
  Start Kaltura session
Start a new Kaltura session, so that new media can be recorded and uploaded
to
this Canvas instance's Kaltura instance.
    `,
  parameters: startKalturaSessionDataSchema.omit({ url: true }),
  execute: async (args : Omit<StartKalturaSessionData, "url"> ) => {
    try {
      const { data } = await startKalturaSession(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    