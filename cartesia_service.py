from contextlib import asynccontextmanager
from cartesia import AsyncCartesia
import asyncio
import pyaudio


class TTSService:
    def __init__(
        self,
        api_key: str,
        voice_id: str = "79743797-2087-422f-8dc7-86f9efca85f1",
        model_id: str = "sonic-3",
        rate: int = 22050,
    ) -> None:
        self.voice_id: str = voice_id
        self.model_id: str = model_id
        self.rate: int = rate
        self.client = AsyncCartesia(api_key=api_key)
        self.audio = pyaudio.PyAudio()

    @asynccontextmanager
    async def _sound_resource(self):
        """
        Función auxiliar para el manejo del stream de audio
        """

        ws = None
        stream = None

        try:
            ws = await self.client.tts.websocket()
            stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.rate,
                output=True
            )
            yield ws, stream
        finally:
            if stream is not None:
                stream.stop_stream()
                stream.close()
            if ws is not None:
                await ws.close()

    async def start(self, text_generator):
        """
        Emitir audio a partir de un stream de texto asíncrono
        """

        async with self._sound_resource() as (ws, stream):
            text_buffer = ""

            async for text_chunk in text_generator:
                text_buffer += text_chunk

                # Delimitamos una sección de texto producido
                if any(punct in text_chunk for punct in ['.', '!', '?', '\n']) or len(text_buffer) > 100:
                    if text_buffer.strip():
                        async with ws.context() as ctx:
                            await ctx.send(
                                model_id=self.model_id,
                                transcript=text_buffer.strip(),
                                voice={
                                    "mode": "id",
                                    "id": self.voice_id
                                },
                                output_format={
                                    "container": "raw",
                                    "encoding": "pcm_f32le",
                                    "sample_rate": self.rate
                                }
                            )

                            async for output in ctx.receive():
                                buffer = output.audio
                                if buffer and stream:
                                    stream.write(buffer)

                        text_buffer = ""

            # Manejo de texto residual
            if text_buffer.strip():
                async with ws.context() as ctx:
                    await ctx.send(
                        model_id=self.model_id,
                        transcript=text_buffer.strip(),
                        voice={
                            "mode": "id",
                            "id": self.voice_id
                        },
                        output_format={
                            "container": "raw",
                            "encoding": "pcm_f32le",
                            "sample_rate": self.rate
                        }
                    )

                    async for output in ctx.receive():
                        buffer = output.audio
                        if buffer and stream:
                            stream.write(buffer)

    async def start_manually(self):
        """
        Modo manual de prueba para servicio TTS
        """

        async with self._sound_resource() as (ws, stream):
            print("Inicializando prueba manual de servicio TTS... (Escriba 'exit' para terminar)")
            while True:
                text = await asyncio.to_thread(input, "> ")

                if text.lower() == "exit":
                    break
                if not text.strip():
                    continue

                async with ws.context() as ctx:
                    await ctx.send(
                        model_id=self.model_id,
                        transcript=text,
                        voice={
                            "mode": "id",
                            "id": self.voice_id
                        },
                        output_format={
                            "container": "raw",
                            "encoding": "pcm_f32le",
                            "sample_rate": self.rate
                        }
                    )

                    async for output in ctx.receive():
                        buffer = output.audio
                        if buffer and stream:
                            stream.write(buffer)

    async def close(self):
        await self.client.close()
        self.audio.terminate()


class STTService:
    def __init__(
        self,
        api_key: str,
        model_id: str = "ink-whisper",
        language: str = "es",
        rate: int = 16000,
    ) -> None:
        self.model_id = model_id
        self.language = language
        self.rate: int = rate
        self.client = AsyncCartesia(api_key=api_key)
        self.audio = pyaudio.PyAudio()
        self.final_word = "gracias"

    @asynccontextmanager
    async def _microphone_websocket_resources(self):
        """
        Función auxiliar para el manejo del websocket y el micrófono del operador
        """

        ws = None
        stream = None

        try:
            ws = await self.client.stt.websocket(
                model=self.model_id,
                language=self.language,
                encoding="pcm_s16le",
                sample_rate=self.rate,
                min_volume=0.35
            )
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.rate,
                frames_per_buffer=1024,
                input=True
            )

            yield ws, stream
        finally:
            if stream is not None:
                stream.stop_stream()
                stream.close()
            if ws is not None:
                await ws.close()

    async def _send_audio(self, ws, stream, stop_event):
        """
        Envio continuo de chunks de audio al websocket STT
        """

        try:
            while not stop_event.is_set():
                chunk = stream.read(1024, exception_on_overflow=False)
                await ws.send(chunk)
                await asyncio.sleep(0.02)

            await ws.send("finalize")
            await ws.send("done")
        except Exception as e:
            print(f"Error al enviar audio: {e}")
            raise

    async def start_stream(self):
        """
        Generador asíncrono que produce texto transcrito en tiempo real
        """
        stop_event = asyncio.Event()

        async with self._microphone_websocket_resources() as (ws, stream):
            send_task = asyncio.create_task(self._send_audio(ws, stream, stop_event))

            try:
                async for result in ws.receive():
                    if result["type"] == "transcript":
                        text = result["text"]
                        is_final = result["is_final"]

                        if is_final:
                            yield text

                            if self.final_word in text.lower():
                                stop_event.set()
                                break
                    elif result["type"] == "done":
                        break
            finally:
                stop_event.set()
                await send_task

    async def close(self):
        await self.client.close()
        self.audio.terminate()


async def main():
    speaker = TTSService(
        api_key="sk_car_Ea5Xgd6vZ5TH8DuNpPuN6q"
    )
    try:
        #await speaker.start(streamer.start_stream())
        #async for text in streamer.start_stream():
        #    print(f"{text}")
        await speaker.start_manually()
    finally:
        #await streamer.close()
        await speaker.close()

if __name__ == "__main__":
    asyncio.run(main())
