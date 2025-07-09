
import { tool } from "ai";
import { getPandataEventsJwtTokenAndItsExpirationDateDataSchema } from "./aitm.schema.ts";
import { getPandataEventsJwtTokenAndItsExpirationDate, GetPandataEventsJwtTokenAndItsExpirationDateData } from "..";

export default tool({
  description: `
  Get a Pandata Events jwt token and its expiration date
Returns a jwt auth and props token that can
be used to send events to
Pandata.

NOTE: This is currently only available to the mobile developer
keys.
    `,
  parameters: getPandataEventsJwtTokenAndItsExpirationDateDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetPandataEventsJwtTokenAndItsExpirationDateData, "url"> ) => {
    try {
      const { data } = await getPandataEventsJwtTokenAndItsExpirationDate(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    