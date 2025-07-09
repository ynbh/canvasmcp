
import { tool } from "ai";
import { getCourseTimetableDataSchema } from "./aitm.schema.ts";
import { getCourseTimetable, GetCourseTimetableData } from "..";

export default tool({
  description: `
  Get course timetable
Returns the last timetable set by
the
{api:CalendarEventsApiController#set_course_timetable Set a course timetable} endpoint
    `,
  parameters: getCourseTimetableDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetCourseTimetableData, "url"> ) => {
    try {
      const { data } = await getCourseTimetable(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    