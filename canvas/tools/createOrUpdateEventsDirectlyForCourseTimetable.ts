
import { tool } from "ai";
import { createOrUpdateEventsDirectlyForCourseTimetableDataSchema } from "./aitm.schema.ts";
import { createOrUpdateEventsDirectlyForCourseTimetable, CreateOrUpdateEventsDirectlyForCourseTimetableData } from "..";

export default tool({
  description: `
  Create or update events directly for a course timetable
Creates and updates "timetable" events for a
course or course section.
Similar to {api:CalendarEventsApiController#set_course_timetable setting a
course timetable},
but instead of generating a list of events based on a timetable schedule,
this
endpoint expects a complete list of events.
    `,
  parameters: createOrUpdateEventsDirectlyForCourseTimetableDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateOrUpdateEventsDirectlyForCourseTimetableData, "url"> ) => {
    try {
      const { data } = await createOrUpdateEventsDirectlyForCourseTimetable(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    